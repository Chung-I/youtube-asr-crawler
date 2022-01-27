from pathlib import Path
import argparse
import datetime
import re
def process_caption(caption):
    caption = re.sub('[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）：；《）《》“”()»〔〕-]+', '', caption).strip()
    return caption

def get_reco_id_factory(data_dir, extension):
    def get_reco_id(file_path):
        relative_path = str(Path(file_path).relative_to(data_dir))
        return relative_path.replace(extension, "").replace("/", "-")
    return get_reco_id

ts2str = lambda timestamp: f"{(int(timestamp*100)):06}"

def merge_segments(utterances):
    text, start, end = utterances[0]
    for idx, utt in enumerate(utterances[1:]):
        cur_text, cur_start, cur_end = utt
        if cur_start <= end:
            end = cur_end
            text += " " + cur_text
        if cur_start > end or idx == len(utterances) - 2:
            yield text, start, end
            end = cur_end
            text = cur_text
            start = cur_start

def get_utt_id(reco_id, begin_seconds, end_seconds):
    return f"{reco_id}-{ts2str(begin_seconds)}-{ts2str(end_seconds)}"

def parse_vtt_to_utterances(vtt_file, reco_id, begin_offset, end_offset, merge=False):
    data_FMT = '%H:%M:%S.%f'
    output_FMT = '%S.%f'
    origin_time_str = "00:00:00.000"
    origin_time = datetime.datetime.strptime(origin_time_str, data_FMT)
    utterances = []
    with open(vtt_file) as fp:
        lines = fp.readlines()
    for idx in range(len(lines)):
        line = lines[idx]
        line = line.strip()
        match = re.match("(\d+:\d+:\d+.\d+) --> (\d+:\d+:\d+.\d+)", line)
        if match:
            begin_time_str = match.group(1)
            end_time_str = match.group(2)
            try:
                begin_time = datetime.datetime.strptime(begin_time_str, data_FMT)
                end_time   = datetime.datetime.strptime(end_time_str, data_FMT)
            except:
                continue
            if begin_time >= end_time:
                continue
            # write to caption file
            caption = lines[idx+1]
            caption = process_caption(caption)

            #process audio
            begin_offset_timedelta = datetime.timedelta(seconds=begin_offset)
            end_offset_timedelta = datetime.timedelta(seconds=end_offset)
            begin_time = begin_time + begin_offset_timedelta - origin_time
            end_time = end_time + end_offset_timedelta - origin_time
            begin_seconds = begin_time.total_seconds()
            end_seconds = end_time.total_seconds()
            begin_seconds = round(begin_seconds, 2)
            end_seconds = round(end_seconds, 2)
            utterances.append((caption, begin_seconds, end_seconds))
    if merge:
        utterances = merge_segments(utterances)
    detailed_utterances = []
    for utt in utterances:
        caption, begin_seconds, end_seconds = utt
        utt_id = get_utt_id(reco_id, begin_seconds, end_seconds)
        utt = {"utt_id": utt_id, "reco_id": reco_id, "caption": caption, "begin_seconds": begin_seconds, "end_seconds": end_seconds}
        detailed_utterances.append(utt)
    return detailed_utterances

def write_segments(utterances, fp):
    for utt in utterances:
        fp.write(f"{utt['utt_id']} {utt['reco_id']} {utt['begin_seconds']} {utt['end_seconds']}\n")

def write_utt2spk(utterances, fp):
    for utt in utterances:
        utt_id = utt['utt_id']
        fp.write(f"{utt_id} {utt_id}\n")

def write_text(utterances, fp):
    for utt in utterances:
        fp.write(f"{utt['utt_id']} {utt['caption']}\n")


def get_all_audio_text_file_pairs(data_dir, audio_file_extension=".wav", caption_file_extension=".vtt"):
    for audio_file in Path(data_dir).rglob('*'+audio_file_extension):
        caption_file = audio_file.with_suffix(caption_file_extension)
        if caption_file.exists():
            yield audio_file, caption_file

def write_wavscp(reco_id, audio_file, fp):
    fp.write(f"{reco_id} {audio_file}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', help='data directory')
    parser.add_argument('output_dir')
    parser.add_argument('--audio-file-extension', default=".wav", help='audio file extension')
    parser.add_argument('--caption-file-extension', default=".zh-TW.vtt", help='caption file extension')
    parser.add_argument('--begin-offset', type=float, default=0.0, help='global begin offset')
    parser.add_argument('--end-offset', type=float, default=0.0, help='global end offset')
    parser.add_argument('--merge-consecutive-segments', action='store_true', help='merge segments')
    args = parser.parse_args()
    get_reco_id = get_reco_id_factory(args.data_dir, args.audio_file_extension)
    segment_file = open(Path(args.output_dir) / "segments", "w")
    utt2spk_file = open(Path(args.output_dir) / "utt2spk", "w")
    text_file = open(Path(args.output_dir) / "text", "w")
    wavscp_file = open(Path(args.output_dir) / "wav.scp", "w")

    for audio_file, caption_file in get_all_audio_text_file_pairs(args.data_dir, args.audio_file_extension, args.caption_file_extension):
        reco_id = get_reco_id(audio_file)
        utterances = parse_vtt_to_utterances(caption_file, reco_id, args.begin_offset, args.end_offset, args.merge_consecutive_segments)
        write_segments(utterances, segment_file)
        write_utt2spk(utterances, utt2spk_file)
        write_text(utterances, text_file)
        write_wavscp(reco_id, audio_file, wavscp_file)

    segment_file.close()
    utt2spk_file.close()
    text_file.close()
    wavscp_file.close()