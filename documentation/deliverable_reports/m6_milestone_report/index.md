---
title: "Month 6 Milestone Report"
layout: post
date: 2019-04-31
toc: true
---

Link to the PDF version of this report. (TODO - insert link to PDF)

## Overview

This report describes the progress towards AutoMATES milestones at the six month mark.

Phase 1 milestones:

- 1.1a: Demonstrate ability to handle multi-level array indexing and open-ended
  loops
- 2a: Implement grammars for variable dependencies
- 2b: Incorporate existing scientific ontologies
- 3a: Demonstrate PDF -> LaTeX pipeline
- 4a: Deliver initial unified CAG-JSON spec
- 4b: Deliver CAG-JSON spec including associated comments with variables
- 5a: Evaluate on benchmark dataset using BLEU.


## CodeExplorer Webapp
The webapp has been Dockerized and is available from Dockerhub. To pull the
image and run the webapp locally, do the following commands:

```
docker pull adarshp/codex
docker run -p 4000:80 adarshp/codex:latest
```

Then navigate to http://127.0.0.1:4000 in your web browser.

{% include_relative model_analysis.md %}

{% include_relative code_summarization.md %}
