while IFS=" " read -r url name;
do
  echo "$url $name"
  youtube-dl --rm-cache-dir || exit 1;
  yt-dlp -o "$1/$name/%(playlist_index)s.%(ext)s" $opt --download-archive downloaded.txt --no-post-overwrites -ciwx --audio-format wav --write-sub --sub-format srt --limit-rate 10M $url --exec "sox %(filepath)q -r 16000 -c 1 -b 16 tmp.wav && mv tmp.wav %(filepath)q" || exit 1;
done<$2
