package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.DiceValues;
import hlibbabii.yahtzee.model.DiceLayout;

public class NOfAKind extends Combination{

    public static final NOfAKind PAIR = new NOfAKind(2);
    public static final NOfAKind THREE_OF_A_KIND = new NOfAKind(3);
    public static final NOfAKind FOUR_OF_A_KIND = new NOfAKind(4);

    private int n;

    public NOfAKind(int n) {
        this.n = n;
    }

    @Override
    public int earnedScores(DiceLayout diceLayout) {
        for (Integer diceValue : DiceValues.getDescendingIterator()) {
            if (diceLayout.getCount(diceValue) >= this.n) {
                return diceValue * this.n;
            }
        }
        return 0;
    }

    @Override
    public String toString() {
        return n + " Of A Kind";
    }
}
