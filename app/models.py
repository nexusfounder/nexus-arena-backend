import re
from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional, List, Dict, Any

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    email: str = Field(...)
    password: str = Field(..., min_length=12)
    phone_number: Optional[str] = None
    bot_token: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        from .security import validate_strong_password
        valid, msg = validate_strong_password(v)
        if not valid:
            raise ValueError(msg)
        return v

class UserLoginRequest(BaseModel):
    username_or_email: str
    password: str
    two_factor_code: Optional[str] = None
    bot_token: Optional[str] = None

class TwoFactorVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=24)

class TwoFactorDisableRequest(BaseModel):
    current_password: str = Field(...)
    code: str = Field(..., min_length=6, max_length=24)

class UserProfileUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    new_password: Optional[str] = None
    current_password: Optional[str] = None  # Mandatory step-up auth for password/email updates
    two_factor_code: Optional[str] = None  # Mandatory step-up 2FA code if 2FA is enabled

    @field_validator("new_password")
    @classmethod
    def validate_new_pw_strength(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 0:
            if len(v) < 4:
                raise ValueError("New password must be at least 4 characters long.")
        return v

class AdminCredentialsUpdateRequest(BaseModel):
    current_password: str = Field(...)
    new_username: Optional[str] = None
    new_password: Optional[str] = None
    two_factor_code: Optional[str] = None

class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0)
    payout_method: str = "RAZORPAY_UPI"  # RAZORPAY_UPI, STRIPE_CARD, BANK_TRANSFER, PAYPAL
    payout_destination: str = Field(..., min_length=3)
    two_factor_code: str = Field(..., min_length=6, max_length=6)  # Compulsory 2FA for payouts
    idempotency_key: str = Field(...)

class VerifyAccountRequest(BaseModel):
    identifier: str
    code: str

class SendOTPRequest(BaseModel):
    identifier: str  # Phone number or email
    otp_type: str = "PHONE"  # PHONE, EMAIL, LOGIN

class VerifyOTPRequest(BaseModel):
    identifier: str
    code: str

class ResetPasswordRequest(BaseModel):
    account_identifier: str = Field(..., min_length=3)
    otp_code: str = Field(..., min_length=4)
    new_password: str = Field(..., min_length=12)
    authenticator_code: Optional[str] = None  # Google Authenticator TOTP or Master Recovery Key

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter (A-Z).")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter (a-z).")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number (0-9).")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~` ]", v):
            raise ValueError("Password must contain at least one special symbol (!@#$%^&*).")
        return v

class AdminSecurityBindingUpdateRequest(BaseModel):
    bound_email: Optional[str] = None
    bound_phone: Optional[str] = None
    authenticator_code: str = Field(..., min_length=6)

class TournamentCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=128)
    game_id: str
    entry_fee_dollars: Optional[float] = None
    entry_fee: Optional[float] = None
    coin_entry_fee: Optional[int] = 500
    prize_pool_dollars: Optional[float] = None
    prize_pool: Optional[float] = None
    max_participants: int = 8
    format: str = "SINGLE_ELIMINATION"
    rules: Optional[str] = None
    banner_url: Optional[str] = None
    is_teaser: Optional[bool] = False
    registration_opens_at: Optional[str] = None
    registration_deadline: Optional[str] = None
    seeding_type: Optional[str] = "AUTO_MMR"

    @model_validator(mode='after')
    def validate_amounts(self):
        if self.prize_pool is None and self.prize_pool_dollars is None:
            self.prize_pool = 2500.0
        elif self.prize_pool is None:
            self.prize_pool = self.prize_pool_dollars
        
        if self.entry_fee is None and self.entry_fee_dollars is None:
            self.entry_fee = 0.0
        elif self.entry_fee is None:
            self.entry_fee = self.entry_fee_dollars
        return self

class TournamentJoinRequest(BaseModel):
    tournament_id: str
    team_name: Optional[str] = "Solo Squad"
    captain_contact: Optional[str] = None
    idempotency_key: str
    payment_type: Optional[str] = "CASH"  # CASH, COINS, UPI, CARD, NETBANKING, CRYPTO
    payment_details: Optional[Dict[str, Any]] = None

class BuyCoinsRequest(BaseModel):
    package_id: str
    coins: int
    amount: float
    payment_method: str = "UPI"  # UPI, CARD, NETBANKING, CRYPTO
    idempotency_key: str

class ReferralClaimRequest(BaseModel):
    referral_code: str

class QuestClaimRequest(BaseModel):
    quest_id: str

class CoinRedeemRequest(BaseModel):
    reward_type: str  # TOURNAMENT_PASS, WALLET_INR, VALORANT_POINTS, BGMI_UC

class MatchReportRequest(BaseModel):
    match_id: str
    score_a: int
    score_b: int
    evidence_url: Optional[str] = None

class MatchDisputeRequest(BaseModel):
    match_id: str
    reason: str
    evidence_url: Optional[str] = None

class DepositRequest(BaseModel):
    amount_dollars: Optional[float] = None
    amount: Optional[float] = None
    idempotency_key: str
    payment_method: str = "RAZORPAY_UPI"  # RAZORPAY_UPI, STRIPE_CARD, PAYPAL

    @model_validator(mode='after')
    def validate_deposit_amount(self):
        if self.amount is None and self.amount_dollars is None:
            self.amount = 500.0
        elif self.amount is None:
            self.amount = self.amount_dollars
        return self

class StripeChargeTokenRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Deposit amount in USD or account currency")
    payment_token: str = Field(..., min_length=4, max_length=128, description="Safe single-use token from Stripe Elements (e.g. tok_... or pm_...)")
    idempotency_key: str = Field(..., min_length=8, max_length=128, description="Unique client idempotency key")
    currency: Optional[str] = "USD"

class SocialLinkRequest(BaseModel):
    provider: str  # discord, steam, twitch, twitter
    handle_or_id: str

class VideoCreateRequest(BaseModel):
    title: str
    game_id: str
    video_url: str
    thumbnail_url: Optional[str] = None
    is_short: bool = True

class GameCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=64)
    slug: Optional[str] = None
    icon: Optional[str] = "🎯"
    category: Optional[str] = "FPS"
    banner_url: Optional[str] = None
    is_active: Optional[bool] = True

class GameUpdateRequest(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    banner_url: Optional[str] = None
    is_active: Optional[bool] = None

class TicketCreateRequest(BaseModel):
    category: str = Field(..., description="FINANCIAL, MATCH_DISPUTE, ACCOUNT_2FA, BUG_REPORT, GENERAL")
    subject: str = Field(..., min_length=3, max_length=128)
    description: str = Field(..., min_length=10)
    priority: Optional[str] = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    related_id: Optional[str] = None

class TicketResolveRequest(BaseModel):
    status: str = Field(..., description="IN_PROGRESS, RESOLVED, CLOSED, REJECTED")
    resolution: Optional[str] = None
    admin_notes: Optional[str] = None
    refund_amount_dollars: Optional[float] = None

class TournamentPostponeRequest(BaseModel):
    new_start_time: str
    new_registration_deadline: Optional[str] = None
    reason: Optional[str] = "Registration window extended to allow more squads to enter"

class TournamentCancelRequest(BaseModel):
    reason: str = Field(..., min_length=3, description="Cancellation explanation for participants")

class SeedingUpdateRequest(BaseModel):
    seeding_type: str = Field(..., description="AUTO_MMR or MANUAL")
    seed_assignments: Optional[List[dict]] = None

class SectionDelegationUpdateRequest(BaseModel):
    section_key: str
    assigned_username: str
    assigned_manager_title: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    responsibilities: Optional[str] = None

class CustomRoleCreateRequest(BaseModel):
    role_key: str = Field(..., min_length=2, max_length=32)
    title: str = Field(..., min_length=2, max_length=64)
    badge_color: Optional[str] = "cyan"  # cyan, amber, rose, purple, emerald, blue
    description: Optional[str] = None
    can_access_admin: Optional[bool] = False
    can_arbitrate: Optional[bool] = False
    can_organize: Optional[bool] = True
    can_manage_users: Optional[bool] = False

class UserRoleUpdateRequest(BaseModel):
    role: str = Field(..., min_length=2, max_length=64)
    custom_title: Optional[str] = None

class UserStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="ACTIVE or SUSPENDED")
    reason: Optional[str] = None

class LinkGuestRequest(BaseModel):
    new_username: str = Field(..., min_length=3, max_length=32)
    email: str = Field(...)
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = None

class RBIPaymentOrderCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount in INR (₹)")
    purpose: str = Field(..., description="TOURNAMENT_ENTRY, WALLET_TOPUP, or COIN_PURCHASE")
    target_id: Optional[str] = None
    payment_method: Optional[str] = "UPI"  # UPI, CARD, NETBANKING, CRYPTO
    notes: Optional[Dict[str, Any]] = None

class RBIPaymentVerifyRequest(BaseModel):
    order_id: str = Field(..., min_length=5)
    payment_id: str = Field(..., min_length=5)
    signature: str = Field(..., min_length=5)
    purpose: str = Field(..., description="TOURNAMENT_ENTRY, WALLET_TOPUP, or COIN_PURCHASE")
    target_id: Optional[str] = None
    amount: float = Field(..., gt=0)
    payment_method: Optional[str] = "UPI"
    card_token: Optional[str] = None
    card_brand: Optional[str] = None
    masked_pan: Optional[str] = None
    upi_vpa: Optional[str] = None
    bank_name: Optional[str] = None
    team_name: Optional[str] = None



