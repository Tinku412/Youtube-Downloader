from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
from datetime import timedelta
import threading

app = Flask(__name__)

# Global progress tracker
download_progress = {
    'percentage': 0,
    'status': 'Initializing...',
    'complete': False,
    'filename': None
}

def format_size(bytes):
    if not bytes:
        return "Unknown size"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} GB"

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = []
            
            # Add MP3 option
            formats.append({
                'format_id': 'mp3',
                'resolution': 'Audio only',
                'ext': 'mp3',
                'filesize': 'Variable',
                'format_note': 'MP3 Audio'
            })
            
            # Filter and organize formats
            for f in info['formats']:
                # Skip formats without video or audio codecs
                if not f.get('vcodec') or f['vcodec'] == 'none':
                    continue
                    
                # Get filesize (if available)
                filesize = format_size(f.get('filesize', 0)) if f.get('filesize') else 'Unknown size'
                
                # Get video quality details
                resolution = f.get('resolution', 'Unknown')
                fps = f.get('fps', '')
                fps_note = f" {fps}fps" if fps else ""
                
                # Get format details
                ext = f.get('ext', '')
                vcodec = f.get('vcodec', '').split('.')[0]
                acodec = f.get('acodec', 'no audio')
                
                # Create format note
                format_note = []
                if f.get('format_note'):
                    format_note.append(f.get('format_note'))
                if vcodec != 'none':
                    format_note.append(f"[{vcodec}]")
                if acodec != 'none':
                    format_note.append(f"[{acodec}]")
                
                formats.append({
                    'format_id': f['format_id'],
                    'resolution': resolution,
                    'ext': ext,
                    'filesize': filesize,
                    'format_note': f"{' '.join(format_note)}{fps_note}",
                    'has_audio': acodec != 'none',
                    'has_video': vcodec != 'none',
                    'fps': fps,
                    'tbr': f.get('tbr', 0)  # Total bitrate
                })
            
            # Sort formats by resolution and bitrate
            formats[1:] = sorted(
                formats[1:],
                key=lambda x: (
                    int(x['resolution'].split('x')[1]) if 'x' in x['resolution'] else 0,
                    x.get('fps', 0),
                    x.get('tbr', 0)
                ),
                reverse=True
            )
            
            # Group formats by resolution
            grouped_formats = {}
            for fmt in formats[1:]:  # Skip MP3
                res = fmt['resolution']
                if res not in grouped_formats:
                    grouped_formats[res] = []
                grouped_formats[res].append(fmt)
            
            duration_str = str(timedelta(seconds=info['duration'])) if info.get('duration') else 'Unknown'
            
            return {
                'title': info['title'],
                'thumbnail': info['thumbnail'],
                'duration': duration_str,
                'author': info['uploader'],
                'formats': formats,
                'grouped_formats': grouped_formats
            }
        except Exception as e:
            raise Exception(f"Error extracting video info: {str(e)}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_video_info', methods=['POST'])
def video_info():
    try:
        url = request.form['url']
        info = get_video_info(url)
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download-progress')
def get_progress():
    return jsonify(download_progress)

def progress_hook(d):
    """yt-dlp progress hook"""
    global download_progress
    
    if d['status'] == 'downloading':
        try:
            # Calculate download percentage
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total_bytes > 0:
                downloaded = d.get('downloaded_bytes', 0)
                percentage = (downloaded / total_bytes) * 100
                download_progress.update({
                    'percentage': round(percentage, 1),
                    'status': f"Downloading... {d.get('_speed_str', '')}",
                    'complete': False
                })
        except Exception as e:
            print(f"Error updating progress: {str(e)}")
    
    elif d['status'] == 'finished':
        download_progress.update({
            'percentage': 100,
            'status': 'Processing...',
            'complete': False
        })
    
    elif d['status'] == 'error':
        download_progress.update({
            'status': 'Error occurred',
            'complete': True
        })

@app.route('/download', methods=['POST'])
def download_video():
    try:
        global download_progress
        download_progress = {
            'percentage': 0,
            'status': 'Starting download...',
            'complete': False,
            'filename': None
        }

        url = request.form['url']
        format_id = request.form.get('format')
        
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
        
        # Configure yt-dlp options with progress hook
        if format_id == 'mp3':
            ydl_opts = {
                'format': 'bestaudio',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'prefer_ffmpeg': True,
                'keepvideo': False,
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
            }
        else:
            ydl_opts = {
                'format': f'{format_id}+bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
                'postprocessor_args': {
                    'ffmpeg': [
                        '-c:v', 'copy',
                        '-c:a', 'aac',
                        '-b:a', '192k',
                    ],
                },
                'merge_output_format': 'mp4',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if format_id == 'mp3':
                filename = os.path.splitext(filename)[0] + '.mp3'
            else:
                filename = os.path.splitext(filename)[0] + '.mp4'
            
            download_progress.update({
                'percentage': 100,
                'status': 'Complete!',
                'complete': True,
                'filename': filename
            })
            
            return send_file(
                filename,
                as_attachment=True,
                download_name=os.path.basename(filename)
            )
            
    except Exception as e:
        download_progress.update({
            'status': f"Error: {str(e)}",
            'complete': True
        })
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True) 