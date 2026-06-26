# Architecture / 架构

## Stage flow / 阶段流

```mermaid
flowchart LR
  I[intent / 意图] --> S1[① specify]
  S1 -->|contract.json| G1{validate_contract}
  G1 -->|pass| S2[② review]
  G1 -->|fail| S1
  S2 --> G2{coverage_gate}
  G2 -->|pass| S3[③ apply]
  G2 -->|block| S1
  S3 --> G3{gate_check<br/>before code}
  G3 -->|pass| IMPL[implement / 实现]
  G3 -->|fail| S2
  IMPL --> S4[④ verify]
  S4 --> G4{dod_check}
  G4 -->|green| SHIP[ship / 上线]
  G4 -->|red| S2
```

## Contract status lifecycle / 契约状态机

```mermaid
stateDiagram-v2
  [*] --> draft: ① specify
  draft --> reviewed: ② coverage_gate pass
  reviewed --> applied: ③ implemented
  applied --> verified: ④ dod_check pass
  applied --> needs_review: dod_check red
  reviewed --> draft: review blocks
  verified --> [*]
```

## Repo map / 仓库地图

```mermaid
flowchart TD
  ROOT[agent-delivery-kit] --> DOCS[docs/<br/>article + concepts + architecture + adapting]
  ROOT --> KIT[kit/]
  ROOT --> EX[examples/<br/>contract.sample.json]
  KIT --> SK[skills/<br/>specify·review·apply·verify]
  KIT --> SH[shared/<br/>contract-schema·rule-sources·DoD]
  KIT --> CM[commands/]
  KIT --> SC[scripts/<br/>4 gates + tests]
  KIT --> CMAP[context-map.yaml]
  KIT --> EXT[extensions/<br/>dual-track · pipeline-driver]
  SK -. references .-> SH
  SK -. enforced by .-> SC
```

> The contract is authoritative; `context-map.yaml` is navigation only. /
> 契约是事实源;`context-map.yaml` 只做导航。
