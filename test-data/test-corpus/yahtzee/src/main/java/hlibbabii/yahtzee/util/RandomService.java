package hlibbabii.yahtzee.util;

import java.util.Random;

public class RandomService {

    private final Random rand;

    public RandomService() {
        this.rand = new Random();
    }

    public int getRandomDiceNumber() {
        return this.rand.nextInt(6) + 1;
    }
}
