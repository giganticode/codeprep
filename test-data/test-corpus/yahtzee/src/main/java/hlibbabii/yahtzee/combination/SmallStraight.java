package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.DiceValues;
import hlibbabii.yahtzee.model.DiceLayout;

import java.util.Arrays;
import java.util.stream.IntStream;

public class SmallStraight extends Combination {

    public static final SmallStraight SMALL_STRAIGHT = new SmallStraight();

    @Override
    public int earnedScores(DiceLayout diceLayout) {
        int[] sortedRolledNumbers = diceLayout.toSortedNumbers();
        if (Arrays.equals(sortedRolledNumbers, IntStream.range(1, DiceValues.MAX_DICE_VALUE).toArray())) {
            return IntStream.of(sortedRolledNumbers).sum();
        } else {
            return 0;
        }
    }

    @Override
    public String toString() {
        return "Small Straight";
    }
}
