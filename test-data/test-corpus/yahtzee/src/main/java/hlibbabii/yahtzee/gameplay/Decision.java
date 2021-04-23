package hlibbabii.yahtzee.gameplay;

import hlibbabii.yahtzee.model.DiceLayout;
import hlibbabii.yahtzee.combination.Combination;

public class Decision {
    private DiceLayout fixedDiceLayout;
    private Combination combination;

    public Decision(Combination combination) {
        this.combination = combination;
    }

    public Decision(DiceLayout fixedDiceLayout) {
        this.fixedDiceLayout = fixedDiceLayout;
    }

    public static Decision fixLayoutAndRoll(DiceLayout fixedDiceLayout) {
        return new Decision(fixedDiceLayout);
    }

    public boolean isCombinationDecision() {
        return this.combination != null;
    }

    public static Decision decideCombination(Combination combination) {
        return new Decision(combination);
    }

    public Combination getCombination() {
        if (!this.isCombinationDecision()) {
            throw new AssertionError("To get the combination the decision has to be final!");
        }

        return this.combination;
    }

    public DiceLayout getDiceDecidedToLeave() {
        return this.fixedDiceLayout;
    }
}