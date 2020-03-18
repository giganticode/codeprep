package hlibbabii.yahtzee;

import hlibbabii.yahtzee.combination.Combination;
import hlibbabii.yahtzee.gameplay.Decision;
import hlibbabii.yahtzee.model.DiceLayout;

import java.util.Set;

public interface Player {
    Decision makeDecision(DiceLayout diceLayout, DiceLayout fixedDiceLayout, Set<Combination> availableCombinations, int rollsLeft);
}
