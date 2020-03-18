package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.model.DiceLayout;

public class Yahtzee extends Combination {

    public static final Yahtzee YAHTZEE = new Yahtzee();

    private static final int SCORES_FOR_YAHTZEE = 50;

    @Override
    public int earnedScores(DiceLayout diceLayout) {
        return diceLayout.toCounts().keySet().size() == 1 ? SCORES_FOR_YAHTZEE : 0;
    }

    @Override
    public String toString() {
        return "Yahtzee";
    }
}
