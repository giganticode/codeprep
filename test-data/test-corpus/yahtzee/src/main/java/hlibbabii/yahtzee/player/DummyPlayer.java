package hlibbabii.yahtzee.player;

import hlibbabii.yahtzee.Player;
import hlibbabii.yahtzee.gameplay.Decision;
import hlibbabii.yahtzee.model.DiceLayout;
import hlibbabii.yahtzee.combination.Combination;

import java.util.Set;

/**
 * This player rolls the dice as many times as he/she/it can and chooses the first combination which is
 * available (even if will give 0 points and there are other combination which can give more than 0 points).
 */
public class DummyPlayer implements Player {

    @Override
    public Decision makeDecision(DiceLayout diceLayout, DiceLayout fixedDiceLayout, Set<Combination> availableCombinations, int rollsLeft) {
        if (rollsLeft == 0) {
            return Decision.decideCombination(availableCombinations.iterator().next());
//            availableCombinations.stream().map(c -> c.earnedScores(diceLayout)).max(Comparator.comparingInt(a->a));
        } else {
            return Decision.fixLayoutAndRoll(fixedDiceLayout);
        }
    }
}