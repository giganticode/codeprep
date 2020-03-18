package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.DiceValues;
import hlibbabii.yahtzee.model.DiceLayout;

import java.util.Arrays;
import java.util.stream.IntStream;

public class LargeStraight extends Combination {

    public static final LargeStraight LARGE_STRAIGHT = new LargeStraight();

    @Override
    public int earnedScores(DiceLayout diceLayout) {
        int[] sortedRolledNumbers = diceLayout.toSortedNumbers();
        if (Arrays.equals(sortedRolledNumbers, IntStream.range(2, DiceValues.MAX_DICE_VALUE + 1).toArray())) {
            return IntStream.of(sortedRolledNumbers).sum();
        } else {
            return 0;
        }
    }

    @Override
    public String toString() {
        return "Large Straight";
    }
}
