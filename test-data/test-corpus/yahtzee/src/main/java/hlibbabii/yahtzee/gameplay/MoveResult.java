package hlibbabii.yahtzee.gameplay;

import hlibbabii.yahtzee.model.DiceLayout;
import hlibbabii.yahtzee.Player;
import hlibbabii.yahtzee.combination.Combination;

import java.util.Objects;

public class MoveResult {
    private final Player player;
    private final Combination combination;
    private final int score;

    private MoveResult(Player player, Combination combination, int scores) {
        this.player = player;
        this.combination = combination;
        this.score = scores;
    }

    public static MoveResult create(Player player, Decision decision, DiceLayout nonFixedDiceLayout) {
        Combination combination = decision.getCombination();
        int scores = combination.earnedScores(nonFixedDiceLayout);
        return new MoveResult(player, combination, scores);
    }

    public Player getPlayer() {
        return this.player;
    }

    public Combination getCombination() {
        return this.combination;
    }

    public int getScore() {
        return this.score;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || this.getClass() != o.getClass()) return false;
        MoveResult that = (MoveResult) o;
        return this.score == that.score &&
                Objects.equals(this.player, that.player) &&
                Objects.equals(this.combination, that.combination);
    }

    @Override
    public int hashCode() {
        return Objects.hash(this.player, this.combination, this.score);
    }

    @Override
    public String toString() {
        return "MoveResult{" +
                "player=" + player +
                ", combination=" + combination +
                ", score=" + score +
                '}';
    }
}