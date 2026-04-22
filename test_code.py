import pytest
from engagement_engine import EngagementEngine


# --- Fixtures ---

@pytest.fixture
def basic_user():
    return EngagementEngine("user123")

@pytest.fixture
def verified_user():
    return EngagementEngine("vip_user", verified=True)


# --- Initialization ---

def test_init_defaults(basic_user):
    assert basic_user.user_handle == "user123"
    assert basic_user.score == 0.23
    assert basic_user.verified == False

def test_init_verified(verified_user):
    assert verified_user.verified == True


# --- process_interaction ---

def test_like_adds_correct_points(basic_user):
    basic_user.process_interaction("like", 1)
    assert basic_user.score == 1.0

def test_comment_adds_correct_points(basic_user):
    basic_user.process_interaction("comment", 1)
    assert basic_user.score == 5.0

def test_share_adds_correct_points(basic_user):
    basic_user.process_interaction("share", 1)
    assert basic_user.score == 10.0

def test_multiple_count(basic_user):
    basic_user.process_interaction("like", 10)
    assert basic_user.score == 10.0

def test_verified_multiplier(verified_user):
    verified_user.process_interaction("like", 1)
    assert verified_user.score == 1.5

def test_verified_share_multiplier(verified_user):
    verified_user.process_interaction("share", 2)
    assert verified_user.score == 30.0  # 10 * 2 * 1.5

def test_invalid_interaction_type_returns_false(basic_user):
    result = basic_user.process_interaction("dm")
    assert result == False
    assert basic_user.score == 0.0  # score unchanged

def test_valid_interaction_returns_true(basic_user):
    result = basic_user.process_interaction("like")
    assert result == True

def test_negative_count_raises_error(basic_user):
    with pytest.raises(ValueError, match="Negative count"):
        basic_user.process_interaction("like", -1)

def test_zero_count(basic_user):
    basic_user.process_interaction("like", 0)
    assert basic_user.score == 0.0


# --- get_tier ---

def test_tier_newbie_at_zero(basic_user):
    assert basic_user.get_tier() == "Newbie"

def test_tier_newbie_below_100(basic_user):
    basic_user.score = 99.9
    assert basic_user.get_tier() == "Newbie"

def test_tier_influencer_at_100(basic_user):
    basic_user.score = 100
    assert basic_user.get_tier() == "Influencer"

def test_tier_influencer_at_1000(basic_user):
    basic_user.score = 1000
    assert basic_user.get_tier() == "Influencer"

def test_tier_icon_above_1000(basic_user):
    basic_user.score = 1001
    assert basic_user.get_tier() == "Icon"


# --- apply_penalty ---

def test_penalty_reduces_score(basic_user):
    basic_user.score = 100
    basic_user.apply_penalty(1)
    assert basic_user.score == 80.0  # 100 - (100 * 0.20)

def test_penalty_score_floor_is_zero(basic_user):
    basic_user.score = 10
    basic_user.apply_penalty(5)  # 100% reduction
    assert basic_user.score == 0

def test_penalty_over_10_reports_removes_verified(verified_user):
    verified_user.score = 100
    verified_user.apply_penalty(11)
    assert verified_user.verified == False

def test_penalty_exactly_10_reports_keeps_verified(verified_user):
    verified_user.score = 100
    verified_user.apply_penalty(10)
    assert verified_user.verified == True

def test_penalty_zero_reports_no_change(basic_user):
    basic_user.score = 100
    basic_user.apply_penalty(0)
    assert basic_user.score == 100.0