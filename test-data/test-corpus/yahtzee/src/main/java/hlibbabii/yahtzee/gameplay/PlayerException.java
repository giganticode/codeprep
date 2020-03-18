package hlibbabii.yahtzee.gameplay;

public class PlayerException extends RuntimeException {
    public PlayerException(Exception e) {
        super(e);
    }
}