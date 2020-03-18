package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.model.DiceLayout;

public class Numbers extends Combination {

    public static final Combination ACES = new Numbers(1);
    public static final Combination TWOS = new Numbers(2);
    public static final Combination THREES = new Numbers(3);
    public static final Combination FOURS = new Numbers(4);
    public static final Combination FIVES = new Numbers(5);
    public static final Combination SIXES = new Numbers(6);

    private Integer number;

    public Numbers(Integer number) {
        this.number = number;
    }

    @Override
    public int earnedScores(DiceLayout diceLayout) {
        return diceLayout.getCount(this.number) * this.number;
    }

    @Override
    public String toString() {
        return "Number(" + number + ")";
    }
}

