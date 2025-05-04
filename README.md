# py-translator
Simple CLI texts translation program written in Python using googletrans library

# Usage
Ensure that the necessary googletrans version from `requirements.txt` was installed.

When user first runs the `translator.py` file without any parameters, he will see the help message as below:

```
translator.py <parameters>
Parameters:
-f <path> = specify single file path.
	translator.py -f path/to/my/file.txt
-d <path> = specify directory path.
	translator.py -d path/to/my/dir/
-o <path> = specify output directory path(must be located in outputs), if directory contains already translated files, they will be treated as already translated and skipped. It is useful when utility has crashed while translating a large dataset of texts to resume process from the break point.
	translator.py -o checkpoint/
-l = save every translated line to a separate file.
-dl = specify destination language for translation(Ukrainian('uk') by default)
-rc <integer> = specify translation retry count, if googletrans couldn't fetch it first time.
```
translator can be used to translate large datasets into specified by `-dl` flag language, it was created specifically for this task and has functionality to do it in at least minimally pleasant way. Generally, the process is stable(and somewhat slow), but there can be still inconveniences with this, as `googletrans` uses Google Translate AJAX API to translate text, which can deny or close connection at times, needing some amount of retries(specified by `-rc` flag) to fetch translated text. Default retry count is 3, you can increase it for more reliability.
If, even after retrying, translator still failed to fetch text and crashed, you can safely restart it from latest break point by specifying output directtory using `-o` flag:
```
# suppose running translator on some large dataset:
python3 translator.py -d /home/Documents/myEnormousDataset/
# translator does the thing... and fails at some point
# restart from the last file
python3 translator.py -d /home/Documents/myEnormousDataset/ -o outputs/YYYY-MM-DD_HH-MM-SS.NNNNNN/
# translator continues from first untranslated file...
```
Optionally, one can save each translated line from input files/directories by enabling `-l` flag, but this will be less reliable, as "break point" will be harder to deduce, if translator fails.
