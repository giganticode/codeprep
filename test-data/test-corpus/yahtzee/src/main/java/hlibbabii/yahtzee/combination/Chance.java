package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.model.DiceLayout;

import java.util.stream.IntStream;

public class Chance extends Combination {
    public static final Chance CHANCE = new Chance();

    @Override
    public int earnedScores(DiceLayout diceLayout) {
        return IntStream.of(diceLayout.toSortedNumbers()).sum();
    }

    @Override
    public String toString() {
        return "Chance";
    }
}
