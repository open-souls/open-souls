import json

import pytest

from engine import story_state, village


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def strict_season(tmp_path):
    season = tmp_path / "season"
    season.mkdir()
    (season / "season_manifest.yaml").write_text(
        """
version: 1
season: 2
legacy_mode: false
human_decision_required: true
contract:
  primary_reader: "关系向读者"
  platform_assumption: "连载网文"
  opening_promise: "门外有人来"
  core_question: "谁会先付代价"
  reward_mix:
    power: 0.2
    relationship: 0.5
    faction: 0.3
rules:
  min_body_chars: 20
  require_causal_transition: true
  require_hook_evidence: true
""",
        encoding="utf-8",
    )
    (season / "factions.yaml").write_text(
        """version: 1
factions:
  - id: mock-faction
    name: mock
    public_goal: "保持秩序"
    hidden_goal: "保住旧账"
    resources: [记录权]
    red_lines: [旧账公开]
    current_move: "正在施压"
    stance: "制度优先"
""",
        encoding="utf-8",
    )
    write_json(
        season / "decisions" / "next.json",
        {
            "version": 1,
            "options": [
                {
                    "id": "A",
                    "label": "先保住制度位置",
                    "primary_reader": "阵营向读者",
                    "opening": "门外传来公文",
                    "winner": "制度",
                    "loser": "关系",
                    "cost": "失去一次信任",
                    "next_pressure": "关系方要求解释",
                    "reward_mix": {"power": 0.5, "relationship": 0.2, "faction": 0.3},
                    "risk": "关系断裂",
                },
                {
                    "id": "B",
                    "label": "让关系承担代价",
                    "primary_reader": "关系向读者",
                    "opening": "门开了",
                    "winner": "关系",
                    "loser": "制度",
                    "cost": "暴露身份",
                    "next_pressure": "旧账进入场景",
                    "reward_mix": {"power": 0.2, "relationship": 0.5, "faction": 0.3},
                    "risk": "关系破裂",
                },
            ],
        },
    )
    write_json(
        season / "plot_state.json",
        {
            "version": 1,
            "current_pressure": "门外有人来",
            "open_threads": ["谁先付代价"],
            "character_goals": {"A": "留下", "B": "保护"},
            "faction_moves": [],
            "state_updates": [],
            "knowledge": {"public": ["门外有人"]},
            "last_accepted_chapter": 0,
        },
    )
    return season


def test_strict_decision_gate_requires_an_approved_option(tmp_path):
    season = strict_season(tmp_path)

    with pytest.raises(story_state.StoryStateError, match="human decision required"):
        story_state.require_approved_decision(str(season))

    story_state.approve_decision(str(season), "B", "the relationship cost is explicit")
    approved = story_state.require_approved_decision(str(season))
    assert approved["id"] == "B"
    (season / "decisions" / "approved.json").write_text(
        json.dumps({"id": "B", "approved": False}), encoding="utf-8"
    )
    with pytest.raises(story_state.StoryStateError, match="approved=true"):
        story_state.require_approved_decision(str(season))
    assert approved["option"]["opening"] == "门开了"


def test_approved_decision_is_single_use_for_the_next_chapter(tmp_path):
    season = strict_season(tmp_path)
    story_state.approve_decision(str(season), "B", "one chapter only")
    assert story_state.require_approved_decision(str(season))["base_chapter"] == 0

    state = story_state.load_plot_state(season)
    state["last_accepted_chapter"] = 1
    (season / "plot_state.json").write_text(
        json.dumps(state, ensure_ascii=False), encoding="utf-8"
    )
    with pytest.raises(story_state.StoryStateError, match="stale or already consumed"):
        story_state.require_approved_decision(str(season))


def test_strict_schema_requires_a_real_choice_and_world_skeleton(tmp_path):
    season = strict_season(tmp_path)
    assert story_state.validate_season(str(season))["ok"] is True

    options = story_state.load_decision_options(season)
    options["options"] = options["options"][:1]
    write_json(season / "decisions" / "next.json", options)
    result = story_state.validate_season(str(season))
    assert "decisions/next.json requires at least 2 options" in result["errors"]


def test_strict_chapter_contract_requires_causal_evidence(tmp_path):
    season = strict_season(tmp_path)
    body = "门开了。林夙没有退，代价是暴露身份。" * 5
    incomplete = {"canonical": True, "decision_id": "B", "hook_evidence": "门开了"}

    errors = story_state.validate_chapter_contract(incomplete, body, story_state.load_manifest(season))

    assert "causal" in errors
    assert "state_updates" in errors

    complete = {
        **incomplete,
        "causal": {
            "pressure": "门外有人逼近",
            "choice": "林夙留下",
            "cost": "暴露身份",
            "state_change": "关系从试探变成共担",
            "next_pressure": "来客带着旧账返回",
        },
        "state_updates": [{"entity": "林夙", "change": "暴露身份", "evidence": "门开了"}],
        "faction_moves": [{"faction": "f", "move": "施压", "consequence": "旧账进入场景", "stance_change": "从观察转为对抗", "evidence": "门开了"}],
    }
    assert story_state.validate_chapter_contract(complete, body, story_state.load_manifest(season)) == []
    wrong_direction = {**complete, "decision_id": "A"}
    assert "decision_id.not_approved" in story_state.validate_chapter_contract(
        wrong_direction,
        body,
        story_state.load_manifest(season),
        approved_decision_id="B",
    )
    malformed = {
        **complete,
        "state_updates": [{"entity": "林夙", "change": "暴露身份", "evidence": "不存在"}],
        "faction_moves": [{"faction": "unknown", "move": "", "consequence": "", "stance_change": "", "evidence": "不存在"}],
    }
    assert "state_updates.fields_or_evidence" in story_state.validate_chapter_contract(
        malformed, body, story_state.load_manifest(season), faction_ids={"f"}
    )
    assert "faction_moves.fields_or_evidence_or_unknown_faction" in story_state.validate_chapter_contract(
        malformed, body, story_state.load_manifest(season), faction_ids={"f"}
    )


def test_duplicate_numbers_are_reported_without_prompt_multiplication(tmp_path):
    season = tmp_path / "season"
    chronicle = season / "chronicle"
    chronicle.mkdir(parents=True)
    (chronicle / "ch001-old.md").write_text("---\nchapter: 1\n---\nold", encoding="utf-8")
    (chronicle / "ch001-canonical.md").write_text(
        "---\ncanonical: true\nchapter: 1\n---\ncanonical", encoding="utf-8"
    )

    candidates = story_state.chapter_candidates(season)
    selected = story_state.canonical_chapter_files(season)

    assert len(candidates[1]) == 2
    assert selected == [(1, chronicle / "ch001-canonical.md")]


def test_strict_village_tick_stops_before_provider_call(tmp_path, monkeypatch, capsys):
    season = strict_season(tmp_path)
    called = []

    def fail_if_called(*args, **kwargs):
        called.append(True)
        raise AssertionError("provider must not run before human approval")

    monkeypatch.setattr(village.writer, "compose", fail_if_called)
    village.tick(
        {"target_chapter_chars": 20, "newcomer_priority": True, "chapters_per_beat": 1},
        {"A": {}, "B": {}},
        str(season),
        {"season": 2, "title": "test", "genre": "test"},
        {},
        {"beats": ["turn"], "beat": 0, "in_beat": 0},
        0.0,
    )

    assert "generation blocked" in capsys.readouterr().out
    assert called == []
    assert not (season / "chronicle").exists()


def test_approved_strict_mock_round_trip_writes_causal_state(tmp_path, monkeypatch):
    season = strict_season(tmp_path)
    story_state.approve_decision(str(season), "B", "approved for the smoke test")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VILLAGE_MOCK", "1")
    monkeypatch.setattr(village, "pick_cast", lambda *args: (["A", "B"], [], 3))
    monkeypatch.setattr(village, "build_prompt", lambda *args: "姓名: A（他）\n姓名: B（她）")
    monkeypatch.setattr(village.C, "load_state", lambda name: {})
    monkeypatch.setattr(village.SE, "beat_line", lambda arc: "turn")

    village.tick(
        {"target_chapter_chars": 20, "newcomer_priority": True, "chapters_per_beat": 1},
        {"A": {}, "B": {}},
        str(season),
        {"season": 2, "title": "test", "genre": "test", "rating": "safe"},
        {},
        {"beats": ["turn"], "beat": 0, "in_beat": 0},
        0.0,
    )

    chapters = list((season / "chronicle").glob("0001-*.md"))
    assert len(chapters) == 1
    meta, body = story_state.parse_chapter(chapters[0])
    assert meta["decision_id"] == "B"
    assert story_state.validate_chapter_contract(meta, body, story_state.load_manifest(season)) == []
    plot = story_state.load_plot_state(season)
    assert plot["last_accepted_chapter"] == 1
    assert len(plot["state_updates"]) == 1
    consumed = story_state.load_approved_decision(season)
    assert consumed["consumed"] is True
    with pytest.raises(story_state.StoryStateError, match="already consumed"):
        story_state.require_approved_decision(str(season))


def test_commit_rolls_back_all_files_after_downstream_failure(tmp_path, monkeypatch, capsys):
    season = strict_season(tmp_path)
    story_state.approve_decision(str(season), "B", "approved for rollback test")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VILLAGE_MOCK", "1")
    monkeypatch.setattr(village, "pick_cast", lambda *args: (["A", "B"], [], 3))
    monkeypatch.setattr(village, "build_prompt", lambda *args: "姓名: A（他）\n姓名: B（她）")
    monkeypatch.setattr(village.C, "load_state", lambda name: {})
    monkeypatch.setattr(village.SE, "beat_line", lambda arc: "turn")
    original_save_state = village.C.save_state

    def write_then_fail(name, state):
        original_save_state(name, state)
        raise OSError("simulated state write failure")

    monkeypatch.setattr(village.C, "save_state", write_then_fail)
    plot_before = (season / "plot_state.json").read_bytes()
    approved_before = (season / "decisions" / "approved.json").read_bytes()

    village.tick(
        {"target_chapter_chars": 20, "newcomer_priority": True, "chapters_per_beat": 1},
        {"A": {}, "B": {}},
        str(season),
        {"season": 2, "title": "test", "genre": "test", "rating": "safe"},
        {},
        {"beats": ["turn"], "beat": 0, "in_beat": 0},
        0.0,
    )

    assert "rolled back" in capsys.readouterr().out
    assert list((season / "chronicle").glob("*.md")) == []
    assert not (tmp_path / "docs" / "chronicle.json").exists()
    assert not (season / "ties.json").exists()
    assert not (season / "arc.json").exists()
    assert not (tmp_path / "souls" / "A" / "state.json").exists()
    assert not (tmp_path / "souls" / "B" / "state.json").exists()
    assert (season / "plot_state.json").read_bytes() == plot_before
    assert (season / "decisions" / "approved.json").read_bytes() == approved_before
