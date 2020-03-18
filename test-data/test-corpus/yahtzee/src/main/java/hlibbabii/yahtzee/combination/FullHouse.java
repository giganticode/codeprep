package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.gameplay.Game;
import hlibbabii.yahtzee.model.DiceLayout;

import java.util.Collection;
import java.util.stream.IntStream;

public class FullHouse extends Combination {

    public static final FullHouse FULL_HOUSE = new FullHouse();

    @Override
    public int earnedScores(DiceLayout diceLayout) {
        assert 5 == Game.N_DICE;

        Collection<Integer> counts = diceLayout.toCounts().values();
        return counts.contains(2) && counts.contains(3)?
                IntStream.of(diceLayout.toSortedNumbers()).sum():
                0;

    }

    @Override
    public String toString() {
        return "Full House";
    }
}
