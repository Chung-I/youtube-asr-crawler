while IFS=" " read -r url name;
do
  echo "$url $name"
  youtube-dl -o "$1/$name/%(playlist_index)s.%(ext)s" -x --audio-format wav --write-sub --sub-format srt $url || exit 1;
done<$2
