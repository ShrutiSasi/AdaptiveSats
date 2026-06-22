"""
Adaptive Bitcoin Accumulation — Manim Presentation
===================================================
Run all scenes as a single video (high quality):

    manim -qh bitcoin_presentation.py AdaptiveBTCPresentation

Individual scene preview:
    manim -ql bitcoin_presentation.py OpeningScene
"""

from manim import *
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────────
# Dark, data-terminal palette — deep navy canvas, electric-cyan accent,
# warm-amber for purchase signals, crimson for danger/euphoria.

BG          = "#0A0E1A"   # near-black navy canvas
PANEL       = "#111827"   # card surface
BORDER      = "#1E2D45"   # subtle panel border
CYAN        = "#00D4FF"   # primary accent — electric cyan
AMBER       = "#F59E0B"   # purchase / buy signal
CRIMSON     = "#EF4444"   # euphoria / danger
EMERALD     = "#10B981"   # accumulation / opportunity
VIOLET      = "#7C3AED"   # Bayesian / model
TEXT_HI     = "#F8FAFC"   # primary text
TEXT_MID    = "#94A3B8"   # secondary text
TEXT_DIM    = "#475569"   # muted text

# Manim colour objects
C_BG      = ManimColor(BG)
C_PANEL   = ManimColor(PANEL)
C_BORDER  = ManimColor(BORDER)
C_CYAN    = ManimColor(CYAN)
C_AMBER   = ManimColor(AMBER)
C_CRIMSON = ManimColor(CRIMSON)
C_EMERALD = ManimColor(EMERALD)
C_VIOLET  = ManimColor(VIOLET)
C_HI      = ManimColor(TEXT_HI)
C_MID     = ManimColor(TEXT_MID)
C_DIM     = ManimColor(TEXT_DIM)


def set_bg(scene: Scene) -> None:
    scene.camera.background_color = C_BG


def panel_rect(w: float, h: float, radius: float = 0.18) -> RoundedRectangle:
    r = RoundedRectangle(width=w, height=h, corner_radius=radius)
    r.set_fill(C_PANEL, opacity=0.85)
    r.set_stroke(C_BORDER, width=1.4)
    return r


def glow_dot(pos, color=C_CYAN, r=0.09) -> VGroup:
    """A bright centre dot with a soft halo."""
    halo  = Circle(radius=r * 2.8).set_fill(color, opacity=0.15).set_stroke(width=0)
    inner = Circle(radius=r).set_fill(color, opacity=0.95).set_stroke(width=0)
    return VGroup(halo, inner).move_to(pos)


def tag_pill(text_str: str, color=C_CYAN, fs: int = 16) -> VGroup:
    t = Text(text_str, font="Helvetica Neue", font_size=fs, color=color)
    if t.width > 2.6:
        t.set_width(2.6)
    bg = RoundedRectangle(
        width=t.width + 0.28,
        height=t.height + 0.14,
        corner_radius=0.1,
    ).set_fill(color, opacity=0.12).set_stroke(color, width=1.0)
    return VGroup(bg, t)


def h1(text_str: str, size: int = 40) -> Text:
    return Text(text_str, font="Helvetica Neue", font_size=size,
                weight=BOLD, color=C_HI)


def body(text_str: str, size: int = 24) -> Text:
    return Text(text_str, font="Helvetica Neue", font_size=size, color=C_MID)


def accent_underline(mob: Mobject, color=C_CYAN, stroke=2.5) -> Line:
    l = Line(mob.get_left(), mob.get_right(), stroke_width=stroke, color=color)
    l.next_to(mob, DOWN, buff=0.07)
    return l


def slide_counter(n: int, total: int = 9) -> Text:
    t = Text(f"{n:02d} / {total:02d}", font="Helvetica Neue",
             font_size=14, color=C_DIM)
    t.to_corner(DR, buff=0.22)
    return t

def hold(scene: Scene, seconds: float = 4.0) -> None:
    """Longer presentation pause for presenter-led explanation."""
    scene.wait(seconds)


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE 1 — OPENING TITLE
# ─────────────────────────────────────────────────────────────────────────────
class OpeningScene(Scene):
    def construct(self):
        set_bg(self)

        # Subtle grid lines for depth
        grid = VGroup()
        for x in np.arange(-7.5, 8.5, 1.5):
            grid.add(Line([x, -4.5, 0], [x, 4.5, 0],
                          stroke_width=0.4, color=C_BORDER))
        for y in np.arange(-4.5, 5.0, 1.5):
            grid.add(Line([-8, y, 0], [8, y, 0],
                          stroke_width=0.4, color=C_BORDER))
        self.add(grid)

        # Floating bitcoin price ghost curve for atmosphere
        axes_ghost = Axes(
            x_range=[0, 12, 1], y_range=[0, 4, 1],
            x_length=14, y_length=5, tips=False,
        ).set_opacity(0)
        ghost_curve = axes_ghost.plot(
            lambda x: 2 + 0.6 * np.sin(0.7 * x) + 0.4 * np.sin(1.8 * x),
            x_range=[0, 12],
            color=C_CYAN,
            stroke_width=1.2,
            stroke_opacity=0.18,
        )
        self.add(ghost_curve)

        # ── Eyebrow tag ──
        eyebrow = tag_pill("UBC · MDS CAPSTONE  2026", color=C_CYAN, fs=15)
        eyebrow.to_edge(UP, buff=0.55)

        # ── Main title ──
        title_line1 = h1("Adaptive Bitcoin", 52)
        title_line2 = h1("Accumulation", 52)
        title_line2.set_color_by_gradient(C_CYAN, C_EMERALD)
        title = VGroup(title_line1, title_line2).arrange(DOWN, buff=0.12).center()
        title.shift(UP * 0.4)

        # ── Accent bar ──
        accent_bar = Line(ORIGIN, RIGHT * 3.4, stroke_width=2.5, color=C_CYAN)
        accent_bar.next_to(title, DOWN, buff=0.22)

        # ── Subtitle ──
        subtitle = body("HMM-GARCH  ·  Bayesian Networks  ·  Regime-Adaptive DCA", 22)
        subtitle.next_to(accent_bar, DOWN, buff=0.28)

        # ── Core question ──
        question_bg = panel_rect(9.2, 0.88, radius=0.14)
        question_text = Text(
            "Can we beat vanilla DCA by adapting to hidden market regimes?",
            font="Helvetica Neue", font_size=22, color=C_AMBER,
        )
        question = VGroup(question_bg, question_text).arrange(ORIGIN)
        question.next_to(subtitle, DOWN, buff=0.62)

        counter = slide_counter(1)

        # ── Animations ──
        self.play(FadeIn(eyebrow, shift=DOWN * 0.15), run_time=0.7)
        self.play(
            LaggedStart(
                Write(title_line1, run_time=0.9),
                Write(title_line2, run_time=0.9),
                lag_ratio=0.35,
            )
        )
        self.play(
            GrowFromCenter(accent_bar, run_time=0.55),
            FadeIn(subtitle, shift=UP * 0.1, run_time=0.6),
        )
        self.play(FadeIn(question, scale=0.97), run_time=0.7)
        self.add(counter)
        hold(self, 55.0)


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE 2 — TRADITIONAL DCA BASELINE
# ─────────────────────────────────────────────────────────────────────────────
class DCABaselineScene(Scene):
    def construct(self):
        set_bg(self)

        title = h1("Traditional DCA", 40).to_edge(UP, buff=0.5)
        underline = accent_underline(title)

        amounts_val = [1, 1, 1, 1, 1, 1, 1, 1]
        bar_w, bar_gap = 0.58, 0.34
        max_h = 2.0

        bars = VGroup()
        tick_labels = VGroup()
        for i, v in enumerate(amounts_val):
            h = max_h * v
            rect = RoundedRectangle(width=bar_w, height=h, corner_radius=0.07)
            rect.set_fill(C_CYAN, opacity=0.72).set_stroke(C_CYAN, width=0.6)
            bars.add(rect)
            lbl = Text(f"Week {i+1}", font="Helvetica Neue", font_size=13,
                       color=C_DIM)
            tick_labels.add(lbl)

        bars.arrange(RIGHT, buff=bar_gap, aligned_edge=DOWN).center().shift(DOWN * 0.1)
        for i, lbl in enumerate(tick_labels):
            lbl.next_to(bars[i], DOWN, buff=0.12)

        dollar_labels = VGroup()
        for bar in bars:
            d = Text("$100", font="Helvetica Neue", font_size=14,
                     color=C_HI)
            d.next_to(bar, UP, buff=0.1)
            dollar_labels.add(d)

        brace = Brace(bars, direction=DOWN, color=C_MID, buff=0.4)
        brace_text = body("Fixed $100 every week, regardless of market conditions", 22)
        brace_text.next_to(brace, DOWN, buff=0.12)

        counter = slide_counter(2)

        self.play(Write(title), run_time=0.7)
        self.play(Create(underline), run_time=0.4)
        self.play(
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1),
            run_time=1.4,
        )
        self.play(
            LaggedStart(*[FadeIn(d, shift=DOWN * 0.1) for d in dollar_labels], lag_ratio=0.07),
            LaggedStart(*[FadeIn(l) for l in tick_labels], lag_ratio=0.07),
            run_time=1.0,
        )
        self.play(GrowFromCenter(brace), Write(brace_text), run_time=0.9)

        # Highlight inefficiency
        cheap_arrow = Arrow(bars[3].get_top() + UP * 0.6, bars[3].get_top(),
                            color=C_EMERALD, buff=0.05, stroke_width=2.5)
        cheap_note = tag_pill("Dip: buy more", C_EMERALD, 14)
        cheap_note.next_to(cheap_arrow, UP, buff=0.08)
        cheap_note.shift(LEFT * 0.75 + UP * 0.15)

        expensive_arrow = Arrow(bars[6].get_top() + UP * 0.6, bars[6].get_top(),
                                color=C_CRIMSON, buff=0.05, stroke_width=2.5)
        expensive_note = tag_pill("Peak: buy less", C_CRIMSON, 14)
        expensive_note.next_to(expensive_arrow, UP, buff=0.08)
        expensive_note.shift(RIGHT * 0.75 + UP * 0.15)

        self.wait(0.6)
        self.play(
            FadeIn(cheap_arrow), FadeIn(cheap_note),
            bars[3].animate.set_fill(C_EMERALD, opacity=0.7),
            run_time=0.8,
        )
        self.play(
            FadeIn(expensive_arrow), FadeIn(expensive_note),
            bars[6].animate.set_fill(C_CRIMSON, opacity=0.7),
            run_time=0.8,
        )
        self.add(counter)
        hold(self, 10.0)


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE 3 — DCA PROBLEM VISUAL
# ─────────────────────────────────────────────────────────────────────────────
class DCAProblemVisualScene(Scene):
    def construct(self):
        set_bg(self)

        title = h1("The DCA Efficiency Gap", 38).to_edge(UP, buff=0.5)
        underline = accent_underline(title)

        # Price axes
        axes = Axes(
            x_range=[0, 9, 1], y_range=[0.8, 4.8, 1],
            x_length=8.8, y_length=3.2, tips=False,
            axis_config={"color": C_BORDER, "stroke_width": 1.2},
        ).shift(UP * 0.85)
        y_label = Text("BTC Price", font="Helvetica Neue", font_size=17, color=C_DIM)
        y_label.rotate(PI / 2).next_to(axes, LEFT, buff=0.18)

        def price(x):
            return 2.5 + 1.05 * np.sin(0.85 * x) + 0.38 * np.sin(2.1 * x)

        curve = axes.plot(price, x_range=[0, 9],
                          color=C_CYAN, stroke_width=2.2)
        curve_area = axes.get_area(curve, x_range=[0, 9],
                                   color=C_CYAN, opacity=0.06)

        self.play(Write(title), Create(underline), run_time=0.8)
        self.play(Create(axes), FadeIn(y_label), run_time=0.6)
        self.play(Create(curve), FadeIn(curve_area), run_time=1.6)

        # Buy points
        xs = np.linspace(0.8, 8.2, 8)
        dots_fixed = VGroup()
        bars_fixed = VGroup()
        for x in xs:
            y = price(x)
            d = glow_dot(axes.c2p(x, y), C_AMBER, r=0.075)
            b = RoundedRectangle(width=0.3, height=1.0, corner_radius=0.06)
            b.set_fill(C_AMBER, opacity=0.65).set_stroke(C_AMBER, width=0.5)
            b.move_to(DOWN * 2.62 + RIGHT * (x - 4.5) * 0.845)
            dots_fixed.add(d)
            bars_fixed.add(b)

        dca_label = Text("Fixed DCA — identical allocation every period",
                         font="Helvetica Neue", font_size=22, color=C_AMBER)
        dca_label.next_to(bars_fixed, UP, buff=0.28)

        self.play(
            LaggedStart(*[FadeIn(d) for d in dots_fixed], lag_ratio=0.09),
            run_time=0.9,
        )
        self.play(
            Write(dca_label),
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars_fixed], lag_ratio=0.09),
            run_time=1.2,
        )

        # Regime zones on the chart
        cheap_patch = axes.get_area(
            axes.plot(price, x_range=[3.8, 6.0]), x_range=[3.8, 6.0],
            color=C_EMERALD, opacity=0.22,
        )
        cheap_tag = tag_pill("cheap / stressed", C_EMERALD, 16)
        cheap_tag.scale(0.85)
        cheap_tag.move_to(axes.c2p(5.8, 1.05))

        eu_patch = axes.get_area(
            axes.plot(price, x_range=[0.8, 3.0]), x_range=[0.8, 3.0],
            color=C_CRIMSON, opacity=0.18,
        )
        eu_tag = tag_pill("expensive / euphoric", C_CRIMSON, 16)
        eu_tag.scale(0.85)
        eu_tag.move_to(axes.c2p(1.25, 4.45))

        self.play(
            FadeIn(cheap_patch), FadeIn(cheap_tag),
            FadeIn(eu_patch), FadeIn(eu_tag),
            run_time=1.0,
        )

        punchline = Text(
            "Same dollar — very different value. Shouldn't we adjust?",
            font="Helvetica Neue", font_size=23, color=C_HI,
        ).to_edge(DOWN, buff=0.3)
        self.play(Write(punchline), run_time=1.0)

        self.add(slide_counter(3))
        hold(self, 10.0)


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE 4 — MARKET REGIMES
# ─────────────────────────────────────────────────────────────────────────────
class MarketRegimeScene(Scene):
    def construct(self):
        set_bg(self)

        title = h1("Market Regimes Are Hidden", 38).to_edge(UP, buff=0.5)
        underline = accent_underline(title)

        # Three regime cards
        regime_specs = [
            ("Accumulation", C_EMERALD, "cheap", "stress", "buy more"),
            ("Neutral",      C_AMBER,   "fair", "stable", "normal buy"),
            ("Euphoria",     C_CRIMSON, "expensive", "optimism", "buy less"),
        ]

        cards = VGroup()
        for name, color, state_1, state_2, action in regime_specs:
            bg = panel_rect(3.05, 2.25, radius=0.2)
            bg.set_stroke(color, width=1.8)

            dot_ring = Circle(radius=0.24)
            dot_ring.set_fill(color, opacity=0.22).set_stroke(color, width=2)

            name_txt = Text(name, font="Helvetica Neue", font_size=18,
                            weight=BOLD, color=color)
            name_txt.set_width(2.2)

            pill_1 = tag_pill(state_1, color, fs=12)
            pill_2 = tag_pill(state_2, color, fs=12)
            pill_row = VGroup(pill_1, pill_2).arrange(RIGHT, buff=0.14)

            action_txt = Text(action, font="Helvetica Neue", font_size=16,
                              weight=BOLD, color=color)
            action_txt.set_width(1.7)

            content = VGroup(
                dot_ring,
                name_txt,
                pill_row,
                action_txt,
            ).arrange(DOWN, buff=0.16)

            cards.add(VGroup(bg, content).arrange(ORIGIN))

        cards.arrange(RIGHT, buff=0.38).center().shift(UP * 0.2)

        hidden_banner_bg = panel_rect(8.9, 0.82, radius=0.12)
        hidden_banner_bg.set_stroke(C_CYAN, width=1.2)
        hidden_banner_text = Text(
            "Regimes are hidden; HMM infers them from market data.",
            font="Helvetica Neue", font_size=15, color=C_CYAN,
        )
        hidden_banner_text.set_width(7.6)
        hidden_banner = VGroup(hidden_banner_bg, hidden_banner_text).arrange(ORIGIN)
        hidden_banner.next_to(cards, DOWN, buff=0.28)

        observed = Text(
            "Signals used: log-returns · GARCH volatility · MVRV Z-score · Price vs Active",
            font="Helvetica Neue", font_size=14, color=C_DIM,
        )
        observed.set_width(7.8)
        observed.next_to(hidden_banner, DOWN, buff=0.28)

        self.play(Write(title), Create(underline), run_time=0.8)
        self.play(
            LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.22),
            run_time=1.4,
        )
        self.play(FadeIn(hidden_banner, scale=0.97), run_time=0.7)
        self.play(FadeIn(observed), run_time=0.6)

        self.add(slide_counter(4))
        hold(self, 10.0)


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE 5 — HMM-GARCH PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
class HMMGARCHPipelineScene(Scene):
    def construct(self):
        set_bg(self)

        title = h1("Strategy 1 — HMM-GARCH Pipeline", 36).to_edge(UP, buff=0.5)
        underline = accent_underline(title, color=C_EMERALD)

        step_specs = [
            ("Bitcoin\nPrice Data",     C_CYAN,    "01"),
            ("GARCH(1,1)\nVolatility",  C_AMBER,   "02"),
            ("HMM\nRegime",             C_EMERALD, "03"),
            ("Valuation\nSignal",       C_VIOLET,  "04"),
            ("DCA\nWeight",             C_CRIMSON, "05"),
        ]

        nodes = VGroup()
        for label, color, num in step_specs:
            bg = RoundedRectangle(width=2.0, height=1.3, corner_radius=0.16)
            bg.set_fill(PANEL, opacity=0.9).set_stroke(color, width=1.8)
            num_txt = Text(num, font="Helvetica Neue", font_size=13, color=color)
            num_txt.to_corner(UL, buff=0.1).move_to(bg.get_corner(UL) + RIGHT * 0.2 + DOWN * 0.2)
            label_txt = Text(label, font="Helvetica Neue", font_size=17,
                             weight=BOLD, color=C_HI, line_spacing=0.9)
            nodes.add(VGroup(bg, num_txt, label_txt).arrange_submobjects())

        # Re-layout manually so num_txt stays top-left
        node_group = VGroup()
        for i, (label, color, num) in enumerate(step_specs):
            bg = RoundedRectangle(width=2.0, height=1.3, corner_radius=0.16)
            bg.set_fill(PANEL, opacity=0.9).set_stroke(color, width=1.8)
            label_txt = Text(label, font="Helvetica Neue", font_size=17,
                             weight=BOLD, color=C_HI, line_spacing=0.85)
            label_txt.move_to(bg)
            num_txt = Text(num, font="Helvetica Neue", font_size=11, color=color)
            num_txt.move_to(bg.get_corner(UL) + RIGHT * 0.18 + DOWN * 0.18)
            node_group.add(VGroup(bg, label_txt, num_txt))

        node_group.arrange(RIGHT, buff=0.5).shift(UP * 0.2)

        arrows = VGroup(*[
            Arrow(
                node_group[i].get_right(),
                node_group[i + 1].get_left(),
                buff=0.08,
                stroke_width=2.0,
                color=C_BORDER,
                tip_length=0.18,
            )
            for i in range(len(node_group) - 1)
        ])

        # Annotation cards below each node
        annotations = [
            "Raw price data +\nlog-returns",
            "σ² estimated via\nGARCH(1,1)",
            "K=3 hidden\nmarket states",
            "MVRV Z-score +\nPrice vs Active",
            "Final adaptive\nDCA weight",
        ]
        ann_group = VGroup()
        colors = [C_CYAN, C_AMBER, C_EMERALD, C_VIOLET, C_CRIMSON]
        for i, (ann, color) in enumerate(zip(annotations, colors)):
            ann_txt = Text(ann, font="Helvetica Neue", font_size=13,
                           color=C_DIM, line_spacing=0.85)
            ann_txt.next_to(node_group[i], DOWN, buff=0.32)
            ann_group.add(ann_txt)

        formula_bg = panel_rect(8.4, 0.68, radius=0.12)
        formula_bg.set_stroke(C_EMERALD, width=1.2)
        formula_txt = Text(
            "weight = regime × valuation × volatility × trend",
            font="Helvetica Neue", font_size=18, color=C_EMERALD,
        )
        formula = VGroup(formula_bg, formula_txt).arrange(ORIGIN)
        formula.to_edge(DOWN, buff=0.32)

        self.play(Write(title), Create(underline), run_time=0.8)
        self.play(FadeIn(node_group[0]), run_time=0.4)
        for i in range(len(arrows)):
            self.play(
                GrowArrow(arrows[i]),
                FadeIn(node_group[i + 1]),
                run_time=0.45,
            )

        self.play(
            LaggedStart(*[FadeIn(a, shift=UP * 0.1) for a in ann_group], lag_ratio=0.1),
            run_time=1.0,
        )
        self.play(FadeIn(formula, scale=0.97), run_time=0.7)

        self.add(slide_counter(5))
        hold(self, 12.0)


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE 6 — HMM-GARCH SIGNAL FLOW (deep-dive)
# ─────────────────────────────────────────────────────────────────────────────
class HMMGARCHSignalFlowScene(Scene):
    def construct(self):
        set_bg(self)

        title = h1("From Market Data → DCA Weight", 36).to_edge(UP, buff=0.48)
        underline = accent_underline(title, color=C_CYAN)

        # ── Price curve ──
        axes = Axes(
            x_range=[0, 10, 1], y_range=[0.5, 4.2, 1],
            x_length=8.5, y_length=2.5, tips=False,
            axis_config={"color": C_BORDER, "stroke_width": 1.0},
        ).shift(UP * 1.15)

        def price(x):
            return 2 + 0.75 * np.sin(x) + 0.22 * np.sin(3 * x)

        curve = axes.plot(price, x_range=[0, 10],
                          color=C_CYAN, stroke_width=2.0)
        curve_fill = axes.get_area(curve, x_range=[0, 10],
                                   color=C_CYAN, opacity=0.05)

        price_lbl = Text("BTC log-returns → GARCH volatility",
                         font="Helvetica Neue", font_size=16, color=C_DIM)
        price_lbl.next_to(axes, UP, buff=0.08)

        self.play(Write(title), Create(underline), run_time=0.7)
        self.play(Create(axes), FadeIn(curve_fill), run_time=0.5)
        self.play(Create(curve), Write(price_lbl), run_time=1.2)

        # Volatility cluster pulses
        cluster_xs = [2.1, 5.3, 8.1]
        pulses = VGroup(*[
            Circle(radius=0.25)
            .set_fill(C_AMBER, opacity=0.0)
            .set_stroke(C_AMBER, width=2.0)
            .move_to(axes.c2p(x, price(x)))
            for x in cluster_xs
        ])
        vol_lbl = Text("GARCH detects volatility clusters",
                       font="Helvetica Neue", font_size=19, color=C_AMBER)
        vol_lbl.next_to(axes, DOWN, buff=0.18)

        self.play(Write(vol_lbl))
        self.play(FadeIn(pulses), run_time=0.4)
        hold(self, 8.0)
        for p in pulses:
            self.play(Indicate(p, color=C_AMBER, scale_factor=2.2), run_time=0.55)

        # ── Regime probability bars ──
        prob_specs = [
            ("Accumulation", 0.68, C_EMERALD),
            ("Neutral",       0.22, C_AMBER),
            ("Euphoria",      0.10, C_CRIMSON),
        ]
        bar_w_full = 2.8

        prob_rows = VGroup()
        fill_rects = VGroup()
        for label_str, prob, color in prob_specs:
            label_m = Text(label_str, font="Helvetica Neue", font_size=17,
                           color=color)
            label_m.set_width(1.5)
            outline = Rectangle(width=bar_w_full, height=0.22)
            outline.set_stroke(C_BORDER, width=1.0).set_fill(opacity=0)
            fill = Rectangle(width=bar_w_full * prob, height=0.22)
            fill.set_fill(color, opacity=0.8).set_stroke(width=0)
            fill.align_to(outline, LEFT)
            pct = Text(f"{int(prob*100)}%", font="Helvetica Neue",
                       font_size=17, color=color)
            row = VGroup(label_m, outline, fill, pct).arrange(RIGHT, buff=0.22)
            prob_rows.add(row)
            fill_rects.add(fill)

        prob_title = Text("HMM regime probabilities  (current timestep)",
                          font="Helvetica Neue", font_size=19, color=C_DIM)
        prob_rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        prob_block = VGroup(prob_title, prob_rows).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        prob_block.next_to(axes, DOWN, buff=0.42)
        prob_block.set_width(5.2)

        self.play(FadeOut(vol_lbl), run_time=0.4)
        self.play(Write(prob_title), run_time=0.6)
        self.play(
            LaggedStart(*[FadeIn(row[0]) for row in prob_rows], lag_ratio=0.14),
            LaggedStart(*[Create(row[1]) for row in prob_rows], lag_ratio=0.14),
            run_time=0.7,
        )
        self.play(
            LaggedStart(*[GrowFromEdge(f, LEFT) for f in fill_rects], lag_ratio=0.2),
            LaggedStart(*[FadeIn(row[3]) for row in prob_rows], lag_ratio=0.2),
            run_time=1.0,
        )
        self.wait(0.4)

        # ── Consolidate → weight ──
        self.play(
            FadeOut(axes), FadeOut(curve), FadeOut(curve_fill), FadeOut(price_lbl),
            FadeOut(pulses),
            run_time=0.7,
        )
        self.play(prob_block.animate.move_to(UP * 1.65).scale(0.72), run_time=0.9)

        weight_bg = panel_rect(4.7, 0.82, radius=0.16)
        weight_bg.set_stroke(C_EMERALD, width=1.8)
        weight_txt = Text("DCA weight = 1.65×",
                          font="Helvetica Neue", font_size=21, color=C_EMERALD)
        weight = VGroup(weight_bg, weight_txt).arrange(ORIGIN)
        weight.move_to(DOWN * 0.55)

        arr = Arrow(prob_block.get_bottom(), weight.get_top(),
                    buff=0.12, stroke_width=2.0, color=C_MID, tip_length=0.2)
        self.play(GrowArrow(arr), run_time=0.5)
        self.play(FadeIn(weight, scale=0.97), run_time=0.6)

        conclusion = Text(
            "More capital is allocated when regime and valuation signals align.",
            font="Helvetica Neue", font_size=18, color=C_DIM,
        )
        conclusion.set_width(8.5)
        conclusion.next_to(weight, DOWN, buff=0.45)
        self.play(Write(conclusion), run_time=1.0)

        self.add(slide_counter(6))
        hold(self, 14.0)


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE 7 — BAYESIAN NETWORK PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
class BayesianPipelineScene(Scene):
    def construct(self):
        set_bg(self)

        title = h1("Strategy 2 — HMM-Bayesian Network", 36).to_edge(UP, buff=0.5)
        underline = accent_underline(title, color=C_VIOLET)

        evidence_specs = [
            ("Valuation State",      C_EMERALD),
            ("Volatility State",     C_AMBER),
            ("Active Price State",   C_CYAN),
            ("HMM Regime",          C_VIOLET),
        ]

        ev_nodes = VGroup()
        for label, color in evidence_specs:
            bg = RoundedRectangle(width=2.8, height=0.68, corner_radius=0.12)
            bg.set_fill(PANEL, opacity=0.9).set_stroke(color, width=1.5)
            txt = Text(label, font="Helvetica Neue", font_size=18,
                       weight=BOLD, color=color)
            ev_nodes.add(VGroup(bg, txt).arrange(ORIGIN))

        ev_nodes.arrange(DOWN, buff=0.24).to_edge(LEFT, buff=0.85).shift(DOWN * 0.3)
        ev_title = Text("Observed evidence nodes",
                        font="Helvetica Neue", font_size=17, color=C_DIM)
        ev_title.next_to(ev_nodes, UP, buff=0.2)

        # Central network box
        net_bg = RoundedRectangle(width=3.2, height=2.6, corner_radius=0.22)
        net_bg.set_fill(PANEL, opacity=0.9).set_stroke(C_VIOLET, width=2.0)
        net_inner = Text("Bayesian\nNetwork\n(pgmpy)", font="Helvetica Neue",
                         font_size=22, weight=BOLD, color=C_VIOLET, line_spacing=0.9)
        network = VGroup(net_bg, net_inner).arrange(ORIGIN)
        network.move_to(RIGHT * 0.8 + DOWN * 0.25)

        # Probability meter
        meter_h = 2.8
        meter_bg = RoundedRectangle(width=0.7, height=meter_h, corner_radius=0.14)
        meter_bg.set_stroke(C_BORDER, width=1.4).set_fill(PANEL, opacity=0.7)
        fill_pct = 0.78
        meter_fill = Rectangle(width=0.6, height=meter_h * fill_pct)
        meter_fill.set_fill(C_EMERALD, opacity=0.8).set_stroke(width=0)
        meter_fill.align_to(meter_bg, DOWN)
        meter = VGroup(meter_bg, meter_fill).to_edge(RIGHT, buff=0.9).shift(DOWN * 0.3)

        prob_lbl = Text("P(opportunity)",
                        font="Helvetica Neue", font_size=18, color=C_DIM)
        prob_lbl.next_to(meter, UP, buff=0.22)
        prob_val = Text("78%", font="Helvetica Neue", font_size=42,
                        weight=BOLD, color=C_EMERALD)
        prob_val.next_to(meter, DOWN, buff=0.2)

        arrows_to_net = VGroup(*[
            Arrow(node.get_right(), network.get_left(), buff=0.1,
                  stroke_width=1.6, color=C_BORDER, tip_length=0.16)
            for node in ev_nodes
        ])
        arr_to_meter = Arrow(network.get_right(), meter.get_left(),
                             buff=0.12, stroke_width=2.0, color=C_VIOLET,
                             tip_length=0.18)

        self.play(Write(title), Create(underline), run_time=0.7)
        self.play(Write(ev_title), run_time=0.4)
        self.play(
            LaggedStart(*[FadeIn(n, shift=RIGHT * 0.2) for n in ev_nodes], lag_ratio=0.18),
            run_time=0.9,
        )
        for a in arrows_to_net:
            self.play(GrowArrow(a), run_time=0.28)
        self.play(FadeIn(network, scale=0.95), run_time=0.6)
        self.play(GrowArrow(arr_to_meter), run_time=0.4)
        self.play(
            Create(meter_bg), Write(prob_lbl), run_time=0.5,
        )
        self.play(
            GrowFromEdge(meter_fill, DOWN),
            FadeIn(prob_val, scale=0.8),
            run_time=1.0,
        )

        self.add(slide_counter(7))
        hold(self, 12.0)


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE 8 — BAYESIAN EVIDENCE FLOW (allocation derivation)
# ─────────────────────────────────────────────────────────────────────────────
class BayesianEvidenceFlowScene(Scene):
    def construct(self):
        set_bg(self)

        title = h1("Bayesian Inference → Allocation", 36).to_edge(UP, buff=0.48)
        underline = accent_underline(title, color=C_VIOLET)

        self.play(Write(title), Create(underline), run_time=0.7)

        # Evidence pills
        evidence_specs = [
            ("Valuation:  cheap (MVRV < 1)",         C_EMERALD),
            ("Volatility: high  (top quartile)",      C_CRIMSON),
            ("Active price:  below realized cost",    C_CYAN),
            ("HMM regime:  Accumulation (p = 0.68)", C_VIOLET),
        ]
        ev_pills = VGroup()
        for text_str, color in evidence_specs:
            pill_bg = RoundedRectangle(width=4.8, height=0.58, corner_radius=0.12)
            pill_bg.set_fill(color, opacity=0.1).set_stroke(color, width=1.2)
            pill_txt = Text(text_str, font="Helvetica Neue", font_size=14,
                            color=color)
            pill_txt.set_width(4.25)
            ev_pills.add(VGroup(pill_bg, pill_txt).arrange(ORIGIN))

        ev_pills.arrange(DOWN, buff=0.18).to_edge(LEFT, buff=0.45).shift(DOWN * 0.45)
        ev_header = Text("Evidence", font="Helvetica Neue", font_size=15, color=C_DIM)
        ev_header.next_to(ev_pills, UP, buff=0.18)

        # Network node centre
        net_circle = Circle(radius=1.0)
        net_circle.set_fill(PANEL, opacity=0.9).set_stroke(C_VIOLET, width=2.2)
        net_inner = VGroup(
            Text("Bayesian", font="Helvetica Neue", font_size=18,
                 weight=BOLD, color=C_VIOLET),
            Text("Network", font="Helvetica Neue", font_size=18,
                 weight=BOLD, color=C_VIOLET),
        ).arrange(DOWN, buff=0.08).move_to(net_circle)
        net = VGroup(net_circle, net_inner).move_to(RIGHT * 1.25 + DOWN * 0.35)

        arrows_in = VGroup(*[
            Arrow(pill.get_right(), net.get_left(), buff=0.1,
                  stroke_width=1.6, color=C_BORDER, tip_length=0.14)
            for pill in ev_pills
        ])

        # Probability bar
        # Build the fill, outline, and percentage as one locked group.
        # This avoids the fill being moved outside the outline by later VGroup arrange calls.
        bar_width = 2.7
        bar_height = 0.48
        fill_width = bar_width * 0.78

        bar_outline = RoundedRectangle(width=bar_width, height=bar_height, corner_radius=0.08)
        bar_outline.set_stroke(C_BORDER, width=1.2)
        bar_outline.set_fill(C_PANEL, opacity=0.65)

        bar_fill = RoundedRectangle(width=fill_width, height=bar_height - 0.12, corner_radius=0.06)
        bar_fill.set_fill(C_EMERALD, opacity=0.82)
        bar_fill.set_stroke(width=0)
        bar_fill.move_to(bar_outline.get_center())
        bar_fill.align_to(bar_outline, LEFT)
        bar_fill.shift(RIGHT * 0.06)

        bar_pct = Text("78%", font="Helvetica Neue", font_size=15,
                       weight=BOLD, color=C_HI)
        bar_pct.move_to(bar_outline.get_center())

        bar_group = VGroup(bar_outline, bar_fill, bar_pct)

        prob_lbl = Text("P(accumulation opportunity)",
                        font="Helvetica Neue", font_size=14, color=C_DIM)
        prob_lbl.next_to(bar_group, UP, buff=0.14)

        prob_block = VGroup(prob_lbl, bar_group)
        prob_block.next_to(net, RIGHT, buff=0.42).shift(UP * 0.12)

        arr_out = Arrow(net.get_right(), prob_block.get_left(),
                        buff=0.12, stroke_width=2.0, color=C_VIOLET, tip_length=0.18)

        # Final weight
        weight_bg = panel_rect(4.5, 0.72, radius=0.16)
        weight_bg.set_stroke(C_EMERALD, width=1.8)
        weight_txt = Text("Final DCA weight = 2.05×",
                          font="Helvetica Neue", font_size=19, color=C_EMERALD)
        weight = VGroup(weight_bg, weight_txt).arrange(ORIGIN)
        weight.to_edge(DOWN, buff=0.78)

        arr_final = Arrow(prob_block.get_bottom(), weight.get_top(),
                          buff=0.12, stroke_width=1.8, color=C_DIM, tip_length=0.18)

        self.play(Write(ev_header), run_time=0.3)
        self.play(
            LaggedStart(*[FadeIn(p, shift=RIGHT * 0.15) for p in ev_pills], lag_ratio=0.17),
            run_time=0.9,
        )
        for a in arrows_in:
            self.play(GrowArrow(a), run_time=0.22)
        self.play(FadeIn(net, scale=0.92), run_time=0.55)
        self.play(GrowArrow(arr_out), run_time=0.4)
        self.play(
            Write(prob_lbl),
            Create(bar_outline),
            GrowFromEdge(bar_fill, LEFT),
            FadeIn(bar_pct),
            run_time=0.9,
        )
        self.play(GrowArrow(arr_final), FadeIn(weight, scale=0.97), run_time=0.6)

        conclusion = Text(
            "When the evidence aligns, the strategy increases the buy size.",
            font="Helvetica Neue", font_size=17, color=C_DIM,
        )
        conclusion.set_width(8.5)
        conclusion.next_to(weight, DOWN, buff=0.25)
        self.play(Write(conclusion), run_time=1.0)

        self.add(slide_counter(8))
        hold(self, 14.0)


# ─────────────────────────────────────────────────────────────────────────────
#  SCENE 9 — CLOSING INSIGHT
# ─────────────────────────────────────────────────────────────────────────────
class ClosingScene(Scene):
    def construct(self):
        set_bg(self)

        # Subtle ambient grid
        grid = VGroup()
        for x in np.arange(-7.5, 8.5, 2.0):
            grid.add(Line([x, -4.5, 0], [x, 4.5, 0],
                          stroke_width=0.3, color=C_BORDER))
        for y in np.arange(-4.5, 5.0, 2.0):
            grid.add(Line([-8, y, 0], [8, y, 0],
                          stroke_width=0.3, color=C_BORDER))
        self.add(grid)

        # Core insight card
        card_bg = panel_rect(9.8, 4.8, radius=0.28)
        card_bg.set_stroke(C_CYAN, width=1.4)

        heading = Text("Core Insight", font="Helvetica Neue", font_size=16,
                       color=C_CYAN)
        accent_bar = Line(ORIGIN, RIGHT * 7.0, stroke_width=1.4, color=C_CYAN)

        line1 = Text(
            "Adaptive DCA does not predict tomorrow's price.",
            font="Helvetica Neue", font_size=26, weight=BOLD, color=C_HI,
        )
        line2 = Text(
            "It identifies conditions that historically resemble",
            font="Helvetica Neue", font_size=23, color=C_MID,
        )
        line3 = Text(
            "high-value accumulation windows — and buys more.",
            font="Helvetica Neue", font_size=23, color=C_MID,
        )

        pillar_specs = [
            ("Regime\nAwareness",    C_EMERALD),
            ("Valuation\nContext",   C_AMBER),
            ("Volatility\nStructure",C_CYAN),
            ("Bayesian\nInference",  C_VIOLET),
        ]
        pillars = VGroup()
        for label, color in pillar_specs:
            bg = RoundedRectangle(width=1.9, height=1.1, corner_radius=0.14)
            bg.set_fill(color, opacity=0.12).set_stroke(color, width=1.4)
            txt = Text(label, font="Helvetica Neue", font_size=15,
                       weight=BOLD, color=color, line_spacing=0.85)
            pillars.add(VGroup(bg, txt).arrange(ORIGIN))
        pillars.arrange(RIGHT, buff=0.3)

        equals = Text("=  Smarter Accumulation",
                      font="Helvetica Neue", font_size=22,
                      weight=BOLD, color=C_EMERALD)

        inner = VGroup(heading, accent_bar, line1, line2, line3, pillars, equals)
        inner.arrange(DOWN, buff=0.28)
        inner.move_to(card_bg)
        inner.shift(DOWN * 0.06)

        card = VGroup(card_bg, inner)
        card.center()

        self.play(FadeIn(card_bg, scale=0.97), run_time=0.6)
        self.play(Write(heading), GrowFromCenter(accent_bar), run_time=0.6)
        self.play(Write(line1), run_time=0.9)
        self.play(Write(line2), Write(line3), run_time=1.0)
        self.play(
            LaggedStart(*[FadeIn(p, shift=UP * 0.15) for p in pillars], lag_ratio=0.18),
            run_time=0.9,
        )
        self.play(Write(equals), run_time=0.7)

        counter_txt = slide_counter(9)
        self.add(counter_txt)

        # Final glow pulse on the card border
        glow_outline = card_bg.copy()
        glow_outline.set_stroke(C_CYAN, width=3.5, opacity=0.0)
        self.add(glow_outline)
        self.play(
            glow_outline.animate.set_stroke(opacity=0.7),
            run_time=0.8, rate_func=there_and_back,
        )
        self.remove(glow_outline)
        hold(self, 12.0)


# ─────────────────────────────────────────────────────────────────────────────
#  COMPOSITE SCENE — renders all scenes in sequence as ONE video
# ─────────────────────────────────────────────────────────────────────────────
class AdaptiveBTCPresentation(Scene):
    """
    Run this class to get the full presentation as a single video file:

        manim -qh bitcoin_presentation.py AdaptiveBTCPresentation

    Quality flags:
        -ql   480p  (fast preview)
        -qm   720p
        -qh   1080p (recommended for final)
        -qk   4K
    """

    def construct(self):
        set_bg(self)

        for SceneClass in [
            OpeningScene,
            DCABaselineScene,
            DCAProblemVisualScene,
            MarketRegimeScene,
            HMMGARCHPipelineScene,
            HMMGARCHSignalFlowScene,
            BayesianPipelineScene,
            BayesianEvidenceFlowScene,
            ClosingScene,
        ]:
            SceneClass.construct(self)
            hold(self, 1.0)
            self.clear()