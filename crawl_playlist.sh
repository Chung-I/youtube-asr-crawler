##youtube-dl -o 'datas/%(playlist)s/%(playlist_index)s.%(ext)s' -x --audio-format wav --write-sub --sub-format srt $1
#youtube-dl -o 'datas/%(playlist)s/%(id)s' --skip-download --write-sub --sub-format vtt $1
while IFS= read -r line; do
    youtube-dl -o 'datas/lanseshuilinglong/%(id)s.%(ext)s' -x --audio-format wav --write-sub --sub-format vtt $1"https://www.youtube.com/watch?v=$line"
done < ids.txt
