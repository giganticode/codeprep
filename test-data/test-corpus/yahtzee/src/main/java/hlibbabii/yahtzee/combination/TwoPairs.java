package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.DiceValues;
import hlibbabii.yahtzee.model.DiceLayout;

public class TwoPairs extends Combination {

    public static final TwoPairs TWO_PAIRS = new TwoPairs();

    @Override
    public int earnedScores(DiceLayout diceLayout) {
        int sum = 0;
        for (Integer diceValue: DiceValues.getDescendingIterator()) {
            if (diceLayout.getCount(diceValue) >= 2) {
                if (sum == 0) {
                    sum = diceValue * 2;
                } else {
                    return sum + diceValue * 2;
                }
            }
        }
        return 0;
    }

    @Override
    public String toString() {
        return "Two Pairs";
    }
}
