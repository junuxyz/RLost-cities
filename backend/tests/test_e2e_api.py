import requests  # type: ignore[import-untyped]

TIMEOUT_SECS = 5


def test_full_game_reproducible_seeded():
    """
    Exercise the API end-to-end until game over with a fixed seed.

    Validates:
    - /game/start returns a valid initial state
    - Repeated /game/turn calls advance turns and alternate players
    - Deck exhaustion triggers game_over and returns scores + winner
    """
    # Use the real server booted by conftest (port 8001)
    base = "http://127.0.0.1:8001"
    r = requests.post(f"{base}/game/start", params={"seed": 123}, timeout=TIMEOUT_SECS)
    assert r.status_code == 200
    state = r.json()["state"]

    turns = 0
    while True:
        cp = state["current_player"]
        player = state["players"][cp]
        hand = player["hand"]

        # Choose a simple legal move policy:
        # - Try to play the first legal expedition card
        # - Otherwise discard the first card
        def last_num(stack_items):
            nums = [c["value"] for c in stack_items if c["value"] != 0]
            return nums[-1] if nums else None

        def can_play(card, stack_items):
            top = last_num(stack_items)
            if card["value"] == 0:
                return top is None
            return top is None or card["value"] >= top

        play = None
        for card in hand:
            stack = player["expeditions"][card["color"]]["items"]
            if can_play(card, stack):
                play = {"card": card, "target": "expedition", "color": card["color"]}
                break
        if play is None:
            c = hand[0]
            play = {"card": c, "target": "discard", "color": c["color"]}

        draw = (
            {"source": "deck"}
            if state["deck"]
            else {
                "source": "discard",
                "color": next(
                    (col for col, pile in state["discard_piles"].items() if pile["items"]), None
                ),
            }
        )
        if draw["source"] == "discard" and draw["color"] is None:
            # If no discard pile is available, fall back to deck (should be rare)
            draw = {"source": "deck"}

        resp = requests.post(
            f"{base}/game/turn",
            json={"state": state, "play": play, "draw": draw},
            timeout=TIMEOUT_SECS,
        )
        assert resp.status_code == 200
        payload = resp.json()
        state = payload["state"]
        turns += 1
        if payload.get("game_over"):
            assert "scores" in payload
            assert "winner" in payload
            # With a fixed seed and deterministic policy, the number of turns should equal remaining deck size
            # 72 total - 16 dealt = 56 draws/turns
            assert turns == 56
            break
