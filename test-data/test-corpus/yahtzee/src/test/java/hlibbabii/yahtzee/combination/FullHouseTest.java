package hlibbabii.yahtzee.combination;

import hlibbabii.yahtzee.model.DiceLayout;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class FullHouseTest {
    @Test
    void testFullHouseAllDistinct() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(2,3,4,5,6);
        int actual = FullHouse.FULL_HOUSE.earnedScores(diceLayout);
        assertEquals(0, actual);
    }

    @Test
    void testFullHouseYahtzeePresent() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(2,2,2,2,2);
        int actual = FullHouse.FULL_HOUSE.earnedScores(diceLayout);
        assertEquals(0, actual);
    }

    @Test
    void testFullHouseThreeOfAKindPresent() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(2,2,2,3,4);
        int actual = FullHouse.FULL_HOUSE.earnedScores(diceLayout);
        assertEquals(0, actual);
    }

    @Test
    void testFullHousePositive() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(2,2,2,3,3);
        int actual = FullHouse.FULL_HOUSE.earnedScores(diceLayout);
        assertEquals(12, actual);
    }

}