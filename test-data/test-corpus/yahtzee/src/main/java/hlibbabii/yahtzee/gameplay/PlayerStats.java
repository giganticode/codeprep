package hlibbabii.yahtzee.gameplay;


import hlibbabii.yahtzee.combination.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.stream.Collectors;

public class PlayerStats {

    private static final int NUMBERS_VALUE_REACH_TO_GET_BONUS = 63;
    private static final int BONUS_VALUE = 50;

    private Map<Combination, Integer> combinations;

    private void initAllCombinations() {
        this.combinations = new HashMap<>();
        /* Numbers*/
        this.combinations.put(Numbers.ACES, null);
        this.combinations.put(Numbers.TWOS, null);
        this.combinations.put(Numbers.THREES, null);
        this.combinations.put(Numbers.FOURS, null);
        this.combinations.put(Numbers.FIVES, null);
        this.combinations.put(Numbers.SIXES, null);

        this.combinations.put(NOfAKind.PAIR, null);
        this.combinations.put(NOfAKind.THREE_OF_A_KIND, null);
        this.combinations.put(NOfAKind.FOUR_OF_A_KIND, null);

        this.combinations.put(FullHouse.FULL_HOUSE, null);
        this.combinations.put(TwoPairs.TWO_PAIRS, null);

        this.combinations.put(SmallStraight.SMALL_STRAIGHT, null);
        this.combinations.put(LargeStraight.LARGE_STRAIGHT, null);

        this.combinations.put(Chance.CHANCE, null);
        this.combinations.put(Yahtzee.YAHTZEE, null);
    }

    public PlayerStats() {
        this.initAllCombinations();
    }

    public Set<Combination> getAvailableCombinations() {
        return this.combinations.entrySet().stream().filter(e -> e.getValue() == null).map(Entry::getKey).collect(Collectors.toSet());
    }

    public void put(Combination combination, int score) {
        if (this.combinations.get(combination) != null) {
            throw new AssertionError(String.format("Combination %s has already been played", combination));
        }
        this.combinations.put(combination, score);
    }

    private int getUpperSectionPoints() {
        return this.combinations.entrySet().stream().filter(e -> e.getKey() instanceof Numbers)
                .map(Entry::getValue).mapToInt(e -> e).sum();
    }

    private int getLowerSectionPoints() {
        return this.combinations.entrySet().stream().filter(e -> !(e.getKey() instanceof Numbers))
                .map(Entry::getValue).mapToInt(e -> e).sum();
    }

    private boolean bonusEarned() {
        return this.getUpperSectionPoints() >= NUMBERS_VALUE_REACH_TO_GET_BONUS;
    }

    public Integer getFinalPoints() {
        return this.getLowerSectionPoints() + this.getUpperSectionPoints() + (this.bonusEarned() ? BONUS_VALUE : 0);
    }

    @Override
    public String toString() {
        return "PlayerStats{" +
                "combinations=" + combinations +
                '}';
    }
}