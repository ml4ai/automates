Link to the PDF version of this report. (TODO - insert link to PDF)

## Overview

This report summarizes progress towards AutoMATES milestones at the six month mark, emphasizing changes since the m5 report.


## CodeExplorer Webapp
The webapp has been Dockerized and is available from Dockerhub. To pull the
image and run the webapp locally, do the following commands:

```
docker pull adarshp/codex
docker run -p 4000:80 adarshp/codex:latest
```

Then navigate to http://127.0.0.1:4000 in your web browser.

