package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.model.DiceLayout;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class SmallStraightTest {

    @Test
    void earnedScoresSmallStraight() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(1, 2, 3, 4, 5);
        int actual = new SmallStraight().earnedScores(diceLayout);
        assertEquals(15, actual);
    }

    @Test
    void earnedScoresLargeStraight() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(2, 3, 4, 5, 6);
        int actual = new SmallStraight().earnedScores(diceLayout);
        assertEquals(0, actual);
    }

    @Test
    void earnedScoresNoStraight() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(1,1,1,2,3);
        int actual = new SmallStraight().earnedScores(diceLayout);
        assertEquals(0, actual);
    }
}