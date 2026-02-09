#!/usr/bin/env python3
"""
Valentine Card Generator
Generates personalized interactive scratch-off Valentine cards.
"""

import argparse
import os
from pathlib import Path

THEMES = {
    "pink": {
        "gradient": "linear-gradient(135deg, #ff6b9d 0%, #ff8a9b 50%, #ffc3d0 100%)",
        "scratch": ["#e91e63", "#f06292", "#ec407a"],
        "accent": "#d63384",
        "light": "#fff5f7",
        "message_bg": "linear-gradient(135deg, #fff5f7 0%, #ffe0e6 100%)",
    },
    "red": {
        "gradient": "linear-gradient(135deg, #e53935 0%, #ef5350 50%, #ffcdd2 100%)",
        "scratch": ["#c62828", "#d32f2f", "#e53935"],
        "accent": "#b71c1c",
        "light": "#ffebee",
        "message_bg": "linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%)",
    },
    "purple": {
        "gradient": "linear-gradient(135deg, #9c27b0 0%, #ba68c8 50%, #e1bee7 100%)",
        "scratch": ["#7b1fa2", "#9c27b0", "#ab47bc"],
        "accent": "#6a1b9a",
        "light": "#f3e5f5",
        "message_bg": "linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)",
    },
    "blue": {
        "gradient": "linear-gradient(135deg, #1976d2 0%, #42a5f5 50%, #bbdefb 100%)",
        "scratch": ["#1565c0", "#1976d2", "#2196f3"],
        "accent": "#0d47a1",
        "light": "#e3f2fd",
        "message_bg": "linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)",
    },
    "gold": {
        "gradient": "linear-gradient(135deg, #f9a825 0%, #fbc02d 50%, #fff59d 100%)",
        "scratch": ["#f57f17", "#f9a825", "#fbc02d"],
        "accent": "#e65100",
        "light": "#fffde7",
        "message_bg": "linear-gradient(135deg, #fffde7 0%, #fff59d 100%)",
    },
}

def generate_card(name: str, message: str, time: str, theme: str, hint: str) -> str:
    """Generate the HTML content for a Valentine card."""
    
    t = THEMES.get(theme, THEMES["pink"])
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💝 A Special Message For {name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: {t["gradient"]};
            font-family: 'Georgia', serif;
            overflow: hidden;
        }}
        
        .container {{
            text-align: center;
            padding: 20px;
        }}
        
        h1 {{
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            font-size: 1.8em;
        }}
        
        .scratch-container {{
            position: relative;
            width: 320px;
            height: 200px;
            margin: 0 auto;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .message {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            background: {t["message_bg"]};
            font-size: 1.6em;
            color: {t["accent"]};
            font-weight: bold;
            text-align: center;
            padding: 20px;
            line-height: 1.4;
        }}
        
        #scratchCanvas {{
            position: absolute;
            top: 0;
            left: 0;
            cursor: pointer;
            border-radius: 20px;
        }}
        
        .hint {{
            color: white;
            margin-top: 20px;
            font-style: italic;
            opacity: 0.9;
        }}
        
        .heart {{
            position: fixed;
            font-size: 30px;
            animation: floatHeart 4s ease-in-out infinite;
            pointer-events: none;
            z-index: 1000;
        }}
        
        @keyframes floatHeart {{
            0% {{
                transform: translateY(100vh) rotate(0deg) scale(0);
                opacity: 1;
            }}
            50% {{
                opacity: 1;
            }}
            100% {{
                transform: translateY(-100vh) rotate(720deg) scale(1.5);
                opacity: 0;
            }}
        }}
        
        .final-message {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 40px 60px;
            border-radius: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            z-index: 1001;
            animation: popIn 0.5s ease-out;
            display: none;
        }}
        
        @keyframes popIn {{
            0% {{
                transform: translate(-50%, -50%) scale(0);
                opacity: 0;
            }}
            50% {{
                transform: translate(-50%, -50%) scale(1.1);
            }}
            100% {{
                transform: translate(-50%, -50%) scale(1);
                opacity: 1;
            }}
        }}
        
        .final-message h2 {{
            color: {t["accent"]};
            font-size: 2em;
            margin-bottom: 15px;
        }}
        
        .final-message p {{
            color: {t["scratch"][1]};
            font-size: 1.3em;
        }}
        
        .final-message .time {{
            font-size: 2.5em;
            color: {t["accent"]};
            font-weight: bold;
            margin-top: 10px;
        }}

        .buttons {{
            margin-top: 25px;
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }}

        .btn {{
            padding: 15px 40px;
            font-size: 1.3em;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            font-family: 'Georgia', serif;
            font-weight: bold;
            transition: all 0.3s ease;
        }}

        .btn-yes {{
            background: {t["gradient"]};
            color: white;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }}

        .btn-yes:hover {{
            transform: scale(1.1);
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        }}

        .btn-no {{
            background: #eee;
            color: #999;
        }}

        .btn-no:hover {{
            background: #ddd;
        }}

        .modal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }}

        .modal-content {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            animation: popIn 0.3s ease-out;
            max-width: 90vw;
        }}

        .modal-content h3 {{
            color: {t["accent"]};
            font-size: 1.8em;
            margin-bottom: 20px;
        }}

        .success-message {{
            display: none;
        }}

        .success-message h2 {{
            font-size: 2.5em;
            margin-bottom: 20px;
        }}

        @keyframes shake {{
            0%, 100% {{ transform: translateX(0); }}
            25% {{ transform: translateX(-10px); }}
            75% {{ transform: translateX(10px); }}
        }}

        .shake {{
            animation: shake 0.5s ease-in-out;
        }}
        
        @media (max-width: 400px) {{
            .scratch-container {{
                width: 280px;
                height: 175px;
            }}
            h1 {{
                font-size: 1.4em;
            }}
            .final-message {{
                padding: 30px;
            }}
            .final-message h2 {{
                font-size: 1.5em;
            }}
            .btn {{
                padding: 12px 30px;
                font-size: 1.1em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ You have a special message, {name}! ✨</h1>
        <div class="scratch-container">
            <div class="message">{message}</div>
            <canvas id="scratchCanvas" width="320" height="200"></canvas>
        </div>
        <p class="hint">{hint}</p>
    </div>
    
    <div class="final-message" id="finalMessage">
        <div id="questionSection">
            <h2>💝 {message} 💝</h2>
            <p>Be ready by</p>
            <div class="time">{time}</div>
            <div class="buttons">
                <button class="btn btn-yes" onclick="sayYes()">Yes 💕</button>
                <button class="btn btn-no" onclick="sayNo()">No</button>
            </div>
        </div>
        <div id="successSection" class="success-message">
            <h2>🎉💕 YAY! 💕🎉</h2>
            <p style="font-size: 1.5em; color: {t["accent"]};">See you at {time}!</p>
            <p style="margin-top: 20px; font-size: 3em;">💝💖💗💕❤️</p>
        </div>
    </div>

    <div class="modal" id="areYouSureModal">
        <div class="modal-content">
            <h3 id="areYouSureText">Are you sure?</h3>
            <div class="buttons">
                <button class="btn btn-yes" onclick="finallyYes()">Yes 💕</button>
                <button class="btn btn-no" onclick="stillNo()">No</button>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('scratchCanvas');
        const ctx = canvas.getContext('2d');
        let isDrawing = false;
        let revealed = false;
        let sureCount = 0;
        
        // Resize canvas for mobile
        function resizeCanvas() {{
            const container = document.querySelector('.scratch-container');
            const rect = container.getBoundingClientRect();
            canvas.width = rect.width;
            canvas.height = rect.height;
            initScratchSurface();
        }}
        
        function initScratchSurface() {{
            const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
            gradient.addColorStop(0, '{t["scratch"][0]}');
            gradient.addColorStop(0.5, '{t["scratch"][1]}');
            gradient.addColorStop(1, '{t["scratch"][2]}');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = 'rgba(255,255,255,0.3)';
            ctx.font = '20px serif';
            const hearts = ['💗', '💖', '💕', '❤️', '💝'];
            for (let i = 0; i < 15; i++) {{
                const x = Math.random() * (canvas.width - 20);
                const y = Math.random() * (canvas.height - 20);
                ctx.fillText(hearts[Math.floor(Math.random() * hearts.length)], x, y);
            }}
            
            ctx.fillStyle = 'white';
            ctx.font = 'bold 22px Georgia';
            ctx.textAlign = 'center';
            ctx.fillText('Scratch Here!', canvas.width/2, canvas.height/2 + 8);
        }}
        
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        function scratch(x, y) {{
            ctx.globalCompositeOperation = 'destination-out';
            ctx.beginPath();
            ctx.arc(x, y, 25, 0, Math.PI * 2);
            ctx.fill();
            checkRevealProgress();
        }}
        
        function getPos(e) {{
            const rect = canvas.getBoundingClientRect();
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            return {{
                x: (clientX - rect.left) * (canvas.width / rect.width),
                y: (clientY - rect.top) * (canvas.height / rect.height)
            }};
        }}
        
        function checkRevealProgress() {{
            if (revealed) return;
            
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const pixels = imageData.data;
            let transparent = 0;
            
            for (let i = 3; i < pixels.length; i += 4) {{
                if (pixels[i] < 128) transparent++;
            }}
            
            const percent = (transparent / (pixels.length / 4)) * 100;
            
            if (percent > 50) {{
                revealed = true;
                canvas.style.transition = 'opacity 1s';
                canvas.style.opacity = '0';
                setTimeout(() => {{
                    canvas.style.display = 'none';
                    showCelebration();
                }}, 1000);
            }}
        }}
        
        function showCelebration() {{
            const hearts = ['❤️', '💕', '💖', '💗', '💝', '💘', '💓', '💞'];
            
            for (let i = 0; i < 50; i++) {{
                setTimeout(() => {{
                    const heart = document.createElement('div');
                    heart.className = 'heart';
                    heart.textContent = hearts[Math.floor(Math.random() * hearts.length)];
                    heart.style.left = Math.random() * 100 + 'vw';
                    heart.style.animationDuration = (3 + Math.random() * 3) + 's';
                    heart.style.fontSize = (20 + Math.random() * 30) + 'px';
                    document.body.appendChild(heart);
                    setTimeout(() => heart.remove(), 6000);
                }}, i * 100);
            }}
            
            setTimeout(() => {{
                document.getElementById('finalMessage').style.display = 'block';
            }}, 1500);
        }}

        function sayYes() {{
            showSuccess();
        }}

        function sayNo() {{
            sureCount = 1;
            document.getElementById('areYouSureText').textContent = 'Are you sure?';
            document.getElementById('areYouSureModal').style.display = 'flex';
        }}

        function stillNo() {{
            sureCount++;
            let sures = '';
            for (let i = 0; i < sureCount; i++) sures += ' sure';
            document.getElementById('areYouSureText').textContent = 'Are you' + sures + '??';
            
            const modal = document.querySelector('.modal-content');
            modal.classList.remove('shake');
            void modal.offsetWidth;
            modal.classList.add('shake');
        }}

        function finallyYes() {{
            document.getElementById('areYouSureModal').style.display = 'none';
            showSuccess();
        }}

        function showSuccess() {{
            document.getElementById('questionSection').style.display = 'none';
            document.getElementById('successSection').style.display = 'block';
            
            const hearts = ['❤️', '💕', '💖', '💗', '💝', '💘', '💓', '💞'];
            for (let i = 0; i < 100; i++) {{
                setTimeout(() => {{
                    const heart = document.createElement('div');
                    heart.className = 'heart';
                    heart.textContent = hearts[Math.floor(Math.random() * hearts.length)];
                    heart.style.left = Math.random() * 100 + 'vw';
                    heart.style.animationDuration = (3 + Math.random() * 3) + 's';
                    heart.style.fontSize = (20 + Math.random() * 40) + 'px';
                    document.body.appendChild(heart);
                    setTimeout(() => heart.remove(), 6000);
                }}, i * 50);
            }}
        }}
        
        // Mouse events
        canvas.addEventListener('mousedown', (e) => {{
            isDrawing = true;
            const pos = getPos(e);
            scratch(pos.x, pos.y);
        }});
        
        canvas.addEventListener('mousemove', (e) => {{
            if (!isDrawing) return;
            const pos = getPos(e);
            scratch(pos.x, pos.y);
        }});
        
        canvas.addEventListener('mouseup', () => isDrawing = false);
        canvas.addEventListener('mouseleave', () => isDrawing = false);
        
        // Touch events
        canvas.addEventListener('touchstart', (e) => {{
            e.preventDefault();
            isDrawing = true;
            const pos = getPos(e);
            scratch(pos.x, pos.y);
        }});
        
        canvas.addEventListener('touchmove', (e) => {{
            e.preventDefault();
            if (!isDrawing) return;
            const pos = getPos(e);
            scratch(pos.x, pos.y);
        }});
        
        canvas.addEventListener('touchend', () => isDrawing = false);
    </script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(
        description="Generate personalized Valentine scratch-off cards"
    )
    parser.add_argument("name", help="Recipient's name")
    parser.add_argument(
        "--message",
        default="Will you be my Valentine?",
        help="Hidden message to reveal",
    )
    parser.add_argument(
        "--time", default="2pm", help="Time/date shown after reveal"
    )
    parser.add_argument(
        "--theme",
        default="pink",
        choices=list(THEMES.keys()),
        help="Color theme",
    )
    parser.add_argument(
        "--hint",
        default="Scratch to reveal your message 💖",
        help="Hint text below the card",
    )
    parser.add_argument(
        "--output", "-o", help="Output file path (default: valentine-{name}.html)"
    )

    args = parser.parse_args()

    # Generate output path if not specified
    if not args.output:
        safe_name = args.name.lower().replace(" ", "-")
        args.output = f"valentine-{safe_name}.html"

    # Generate the card
    html = generate_card(
        name=args.name,
        message=args.message,
        time=args.time,
        theme=args.theme,
        hint=args.hint,
    )

    # Write to file
    output_path = Path(args.output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)

    print(f"✅ Generated Valentine card for {args.name}")
    print(f"📍 Saved to: {output_path.absolute()}")
    print(f"🎨 Theme: {args.theme}")
    print(f"💌 Message: {args.message}")
    print(f"⏰ Time: {args.time}")
    print()
    print("To view: open the HTML file in any browser")
    print("To share: send the file or deploy to Cloudflare Pages")


if __name__ == "__main__":
    main()
