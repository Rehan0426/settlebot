---
name: Autonomous Reconciliation & Settlement Interface
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#45464d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#006a61'
  on-secondary: '#ffffff'
  secondary-container: '#86f2e4'
  on-secondary-container: '#006f66'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#00174b'
  on-tertiary-container: '#497cff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#89f5e7'
  secondary-fixed-dim: '#6bd8cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#dbe1ff'
  tertiary-fixed-dim: '#b4c5ff'
  on-tertiary-fixed: '#00174b'
  on-tertiary-fixed-variant: '#003ea8'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  label-lg:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  data-mono-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: -0.01em
  data-mono-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  space-2xs: 0.25rem
  space-xs: 0.5rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  chat-max-width: 54rem
  panel-width: 26rem
  gutter-desktop: 1.5rem
  gutter-mobile: 1rem
---

## Brand & Style

This design system establishes an institutional-grade, high-precision financial operations environment. It balances the computational velocity of AI automation with the uncompromising reliability demanded by corporate treasurers, finance controllers, and compliance teams. The interface delivers absolute clarity over complex multi-rail transactions, ledger inconsistencies, and high-volume settlement pipelines.

The aesthetic philosophy fuses **Modern Corporate Realism** with **Computational Precision**:
- **Clarity over novelty:** Every pixel serves operational comprehension. Distracting gradients or decorative noise are stripped away in favor of crisp delineation, high typographic scanability, and structural certainty.
- **Calm authority:** The visual tempo relies on airy, structured off-whites and cool slates, preventing sensory fatigue during continuous ledger reconciliation.
- **Definitive state awareness:** Machine-learning inferences and bot confidence scores are conveyed through refined, semantic indicators (settled emerald, pending amber, anomaly coral) designed for rapid zero-error scanning.
- **Tactile feedback:** Interactive elements provide subtle, micro-calibrated feedback (border-light shifting, delicate inner rings) that impart the feel of high-end financial machinery.

## Colors

The color architecture is built upon a cool-tinted, light-mode foundation engineered for maximum contrast, eye comfort, and structured information hierarchy.

### Core Canvas & Surfaces
- **Canvas (`#F8FAFC`):** Base workspace and chat thread backdrop, creating a gentle contrast against pure white cards.
- **Surface High (`#FFFFFF`):** Chat messages, interactive floating inspectors, ledger breakout panels, and dropdown controls.
- **Surface Muted (`#F1F5F9`):** Input enclosures, table header rows, and deactivated state backings.
- **Subtle Stroke (`#E2E8F0`):** Hairline partition borders creating clean spatial segregation.
- **Structural Stroke (`#CBD5E1`):** Active card boundaries, focused states, and modal perimeters.

### Typography Hierarchy
- **Text Primary (`#0F172A`):** Ledger totals, critical metrics, query responses, and primary actions.
- **Text Secondary (`#475569`):** Chat prompt metadata, table values, column headers, and conversational context.
- **Text Muted (`#94A3B8`):** Timestamps, UUID transaction hashes, pagination counters, and placeholder states.

### Accent & Semantic Roles
- **Command Accent (`#0F172A` / `#1E293B`):** Deep midnight slate for authoritative primary triggers, system execution bars, and primary interactive nodes.
- **Financial Trust & Success (`#0D9488` / `#10B981`):** Deep emerald/teal denoting verified reconciliations, balanced ledger states, and confirmed settlements.
- **Algorithmic Focus (`#2563EB`):** Precision cobalt blue reserving contextual citations, highlighted AI suggestions, interactive drill-downs, and table row selection.
- **Pending / In Review (`#D97706`):** Balanced ochre for in-flight settlements, batch processing, and awaiting approval notices.
- **Discrepancy / Flagged (`#DC2626`):** High-visibility crimson for mismatched currency adjustments, failed settlement webhooks, and ledger discrepancies.

## Typography

The typography pairings serve distinct cognitive workflows:
1. **Plus Jakarta Sans (Headings & Bot Metrics):** Provides structural solidity with soft geometric terminals, softening high-density financial data while maintaining enterprise authority.
2. **Inter (Body, Narrative & Inquiries):** Engineered for ultra-clean readability in natural language conversation bubbles, automated explanations, and form inputs.
3. **JetBrains Mono (Financial Values, Reference IDs & Timestamps):** Enforces tabular alignment across multi-line ledger outputs, transaction hashes (`txn_9829f0`), clearing house codes, and monetary sums.

### Tabular Alignment Rules
- Currency figures and financial deltas must consistently implement tabular figures (`font-variant-numeric: tabular-nums`) to preserve vertical visual columns across rows.
- Transaction identifiers and ISO codes should strictly utilize `data-mono-sm` to clearly separate human conversation from immutable machine data.

## Layout & Spacing

The design system implements a tri-pane responsive master-detail architecture:
- **Left Rail (Persistent / Collapsible, 280px):** Contextual session history, quick queries, reconciliation batch selectors.
- **Center Workspace (Primary Conversation & Canvas, max 864px / 54rem):** AI chat stream, settlement breakdowns, inline interactive data components, query inputs.
- **Right Rail (Context Inspector / Drawer, 416px / 26rem):** Deep ledger inspection, counterparty trace, raw JSON audit logs, and approval triggers.

### Spacing Philosophy
- Base layout rhythm aligns strictly with an **8px linear scale** (with 4px increments for tightly-coupled micro-components like status tags and table cells).
- **Chat Feed Geometry:** Conversation messages maintain `1.5rem (24px)` vertical separation. Internal message block padding adheres to `1rem (16px)` horizontal and vertical padding for consistent density.
- **Data Table Layout:** Compact padding with `0.5rem (8px)` vertical and `0.75rem (12px)` horizontal row limits, maximizing visible record volume without feeling cramped.

### Breakpoints & Adaptability
- **Desktop (>= 1280px):** Full 3-pane experience. Both contextual sidebar and deep audit inspector remain simultaneously viewable.
- **Laptop / Tablet Landscape (1024px - 1279px):** Inspector transitions into a right-anchored slide-over sheet. Workspace expands to 100% remaining width.
- **Mobile (< 768px):** Single-column stack. Sidebar collapses into a top navigation drawer; chat messages span full viewport width minus `1rem` edge margins; tables scroll horizontally with sticky ID anchors.

## Elevation & Depth

Depth is established primarily through **ambient diffusion and structural hairline layering**, avoiding heavy drop shadows to preserve a sterile, premium environment.

### Surface Tiers
- **Tier 0 (Base Canvas):** `#F8FAFC` flat canvas surface.
- **Tier 1 (Cards, Chat Message Cards):** `#FFFFFF` paired with a 1px boundary of `#E2E8F0` and `shadow-subtle` (`0px 1px 2px rgba(15, 23, 42, 0.04), 0px 1px 3px rgba(15, 23, 42, 0.02)`).
- **Tier 2 (Floating Action Bars, Dropdowns, Hovered Rows):** `#FFFFFF` supported by `0px 4px 6px -1px rgba(15, 23, 42, 0.06), 0px 2px 4px -2px rgba(15, 23, 42, 0.04)` and border `#CBD5E1`.
- **Tier 3 (Modals, Contextual Ledger Overlays):** `#FFFFFF` anchored by an ambient elevation of `0px 20px 25px -5px rgba(15, 23, 42, 0.08), 0px 8px 10px -6px rgba(15, 23, 42, 0.04)`.

### Lighting & Boundary Principles
- Pure shadows are never rendered without a corresponding `1px` subtle boundary stroke (`#E2E8F0` or `#EEF2F6`) to prevent blur bleeding against off-white backgrounds.
- High-priority system callouts utilize a soft accent halo (`box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.12)`).

## Shapes

The interface balances precision and modern approachability by employing a controlled **Level 2 (Rounded)** shape token set.

### Geometry Specifications
- **Standard Controls & Badges (`rounded-md` / 8px):** Status badges, inline action chips, table filter selectors, and icon triggers.
- **Primary Input Fields & Context Cards (`rounded-lg` / 12px - 14px):** Form text inputs, conversation chat bubbles, metric cards, and settlement snapshot containers.
- **Chat Dock & Modal Containers (`rounded-xl` / 16px):** Floating prompt input bar, modal frames, and dynamic preview cards.
- **Avatars & System State Markers (`rounded-full`):** User avatars, bot identity chips, and binary status indicators.

### Edge Consistency
- Buttons and form inputs must never use circular pill shapes unless they function as removable filter tags or interactive quick-reply prompts. Structural tools rely on disciplined 10px-14px radiuses to reinforce structural credibility.

## Components

### Buttons
- **Primary:** Dark slate background (`#0F172A`), text `#FFFFFF`, subtle inset top highlight (`box-shadow: inset 0 1px 0 rgba(255,255,255,0.15)`), `0.5rem 1rem` padding, `12px` corner radius. Hover: `#1E293B`. Active: scale `0.985`.
- **Secondary (Settlement/Fintech Accent):** Solid emerald/teal background (`#0D9488`), text `#FFFFFF`, focused on financial reconciliation actions (e.g., "Approve Match", "Release Batch").
- **Subtle / Outline:** Background `#FFFFFF`, 1px border `#CBD5E1`, text `#0F172A`. Hover: background `#F8FAFC`, border `#94A3B8`.

### Chat Bubbles & Conversation Stream
- **User Message:** Self-aligned right. Subtle slate surface (`#F1F5F9`), text `#0F172A`, 1px border `#E2E8F0`, 14px border radius with bottom-right corner tapering to 4px.
- **Bot Response:** Self-aligned left. Crisp pure white surface (`#FFFFFF`), 1px border `#E2E8F0`, subtle shadow, 14px border radius with bottom-left corner tapering to 4px. Houses formatted text, automated breakdown tables, and inline action buttons.
- **AI Citation & Thought Block:** Nested inside bot response; background `#F8FAFC`, left border 2px solid `#2563EB`, text `label-md` `#475569`, tracking logic traces and ledger confidence scores.

### Status Badges
Padded with `0.25rem 0.625rem`, `6px` radius, typography `label-sm`:
- **Settled:** Background `#ECFDF5`, text `#065F46`, 1px border `#A7F3D0`, leading pulse dot in `#10B981`.
- **Pending:** Background `#FFFBEB`, text `#92400E`, 1px border `#FDE68A`, leading solid dot in `#F59E0B`.
- **Flagged / Discrepancy:** Background `#FEF2F2`, text `#991B1B`, 1px border `#FECACA`, leading triangle icon in `#EF4444`.
- **Neutral / Draft:** Background `#F1F5F9`, text `#475569`, 1px border `#CBD5E1`.

### Structured Financial Data Tables
- Embedded directly within conversation streams or expanded in the Context Inspector.
- **Header:** Background `#F8FAFC`, border-bottom 1px solid `#CBD5E1`, uppercase `label-sm` text `#475569`.
- **Row Anatomy:** Alternating or clean hover (`#F8FAFC`), 1px bottom border `#F1F5F9`, numbers right-aligned with `data-mono-md`.
- **Discrepancy Highlighting:** Problematic ledger cells display a delicate red corner tag and pale rose fill (`#FFF1F2`).

### Input Fields & Chat Input Dock
- **Chat Prompt Container:** Floating anchor bar with `16px` radius, background `#FFFFFF`, border 1px solid `#CBD5E1`, elevated by `shadow-md`.
- **States:** Focus-within activates a 1px border `#0D9488` with a `0 0 0 3px rgba(13, 148, 136, 0.15)` focus ring.
- **Auxiliary Controls:** Integrated quick-action prompts ("Show unmatched deposits", "Run netting cycle") styled as rounded-full chips with background `#F1F5F9` and hover background `#E2E8F0`.

### Ledger Comparison Card
- Dual-column comparison widget illustrating Source Ledger vs. Bank Statement values.
- Mismatched fields render in high-contrast monospaced font with direct conflict diff highlighting (`#FEE2E2` vs `#DC2626`).