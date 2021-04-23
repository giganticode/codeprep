package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.model.DiceLayout;
import org.junit.jupiter.api.Test;

import static hlibbabii.yahtzee.combination.TwoPairs.TWO_PAIRS;
import static org.junit.jupiter.api.Assertions.*;

class TwoPairsTest {

    @Test
    void testTwoPairsAllDistinct() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(1, 2, 3, 5, 6);
        int actual = TWO_PAIRS.earnedScores(diceLayout);
        assertEquals(0, actual);
    }

    @Test
    void testTwoPairsOnePairPresent() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(1,2,2,3,4);
        int actual = TWO_PAIRS.earnedScores(diceLayout);
        assertEquals(0, actual);
    }

    @Test
    void testTwoPairsTwoPairsPresent() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(1,1,4,5,5);
        int actual = TWO_PAIRS.earnedScores(diceLayout);
        assertEquals(12, actual);
    }

    @Test
    void testTwoPairsFullHousePresent() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(2,2,2,6,6);
        int actual = TWO_PAIRS.earnedScores(diceLayout);
        assertEquals(16, actual);
    }

    @Test
    void testTwoPairsForOfAKindPresent() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(3,5,5,5,5);
        int actual = TWO_PAIRS.earnedScores(diceLayout);
        assertEquals(0, actual);
    }
}