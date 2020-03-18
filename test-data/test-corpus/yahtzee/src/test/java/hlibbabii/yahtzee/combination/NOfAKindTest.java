package hlibbabii.yahtzee.combination;


import hlibbabii.yahtzee.model.DiceLayout;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class NOfAKindTest {
    @Test
    public void testNoPairs() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(1,2,3,6,5);
        int actual = NOfAKind.PAIR.earnedScores(diceLayout);
        Assertions.assertEquals(0, actual);
    }

    @Test
    public void testHighPair() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(1,2,3,5,5);
        int actual = NOfAKind.PAIR.earnedScores(diceLayout);
        Assertions.assertEquals(10, actual);
    }

    @Test
    public void testMediumPair() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(6,1,2,2,5);
        int actual = NOfAKind.PAIR.earnedScores(diceLayout);
        Assertions.assertEquals(4, actual);
    }

    @Test
    public void testPairLow() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(1,2,3,6,1);
        int actual = NOfAKind.PAIR.earnedScores(diceLayout);
        Assertions.assertEquals(2, actual);
    }

    @Test
    public void testPairTwoPairsPresent() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(6,5,3,3,5);
        int actual = NOfAKind.PAIR.earnedScores(diceLayout);
        Assertions.assertEquals(10, actual);
    }

    @Test
    public void testPairThreeOfAKindPresent() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(2,3,5,3,3);
        int actual = NOfAKind.PAIR.earnedScores(diceLayout);
        Assertions.assertEquals(6, actual);
    }

    @Test
    public void testPairFullHouseHighPresent() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(2,4,4,4,2);
        int actual = NOfAKind.PAIR.earnedScores(diceLayout);
        Assertions.assertEquals(8, actual);
    }

    @Test
    public void testPairFullHouseLowPresent() {
        DiceLayout diceLayout = DiceLayout.fromNumbers(2,4,4,2,2);
        int actual = NOfAKind.PAIR.earnedScores(diceLayout);
        Assertions.assertEquals(8, actual);
    }
}