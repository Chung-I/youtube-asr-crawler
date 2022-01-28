# Youtube ASR Crawler

## Usage

- Each line in `drama_list.txt` is of the format `[url] [playlist_name]`; wavfiles and subtitle file will be saved to `[data_dir]/[playlist_name]/[video_id].{wav,vtt}`.
  - `bash crawl_playlist.sh [data_dir] playlists.txt`

- `process.py` then process `.vtt` files and process it in to kaldi-style data format.
  - `python process.py [data_dir] dir/to/{text,segments,wav.scp,utt2spk} [--merge-consecutive-segments]`
- Timestamps of some of the closed captions are not very accurate, so you might want to `--merge-consecutive-segments` then run something like `segment_long_utterances.sh` to obtain more accurate timestamp of each segments.
