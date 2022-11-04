# antenna
サイトを巡回して更新があったらDiscordに教えてくれる君。

## Usage

task.jsonに以下のように記述。
```json
[
    {
        "task_name": "utc",
        "type": "text",
        "url":"http://worldclockapi.com/api/json/utc/now"
    },
    {
        "task_name": "est",
        "type": "text",
        "url":"http://worldclockapi.com/api/json/est/now",
        "pattern": "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}",
        "disable": true
    },
    {
        "task_name": "oreilly",
        "type": "rss",
        "url": "http://feeds.feedburner.com/oreilly/newbooks",
        "title": "O'Reilly New Books",
        "count": 1
    }
]
```

cronを設定。

```
$ crontab -e
```
```
* * * * * <Pythonの絶対パス> <antenna.pyの絶対パス> --discord_webhook --discord_webhook_url <Discord webhook URL>
```

## Sample Output
```
$ python antenna.py --sample
UPDATED: http://worldclockapi.com/api/json/utc/now
--- Previous
+++ Current
@@ -1 +1 @@
-{"$id":"1","currentDateTime":"2021-11-23T08:40Z", ... 6,"ordinalDate":"2021-327","serviceResponse":null}
+{"$id":"1","currentDateTime":"2021-11-28T16:05Z", ... 0,"ordinalDate":"2021-332","serviceResponse":null}

UPDATED: http://worldclockapi.com/api/json/est/now
--- Previous
+++ Current
@@ -1 +1 @@
-2021-11-28T11:20
+2021-11-28T11:21
```

## Options

```
usage: antenna.py [-h] [--task-file TASK_FILE] [--discord-webhook] [--clear] [--line-length-limit LINE_LENGTH_LIMIT]
                  [--task-name TASK_NAME] [--no-archive] [--show]

options:
  -h, --help            show this help message and exit
  --task-file TASK_FILE
                        URL list (default: task.json)
  --discord-webhook     Post messages to Discord servers (default: False)
  --clear               Clear archive directory (default: False)
  --line-length-limit LINE_LENGTH_LIMIT
                        Line length limit of diff (default: 100)
  --task-name TASK_NAME
                        Select a task (default: None)
  --no-archive          Do not archive sites (default: False)
  --show                Show content (default: False)
```

## 簡易テスト

