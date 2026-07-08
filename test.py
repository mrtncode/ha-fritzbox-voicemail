import os
import sys
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from fritzconnection import FritzConnection
from fritzconnection.lib.fritztam import FritzTAM

# Platform-specific audio player
if sys.platform == "win32":
    import winsound
elif sys.platform == "darwin":
    import subprocess
else:  # Linux
    import subprocess

load_dotenv()

fc = FritzConnection(
    address=os.getenv("FRITZ_ADDRESS"),
    user=os.getenv("FRITZ_USER"),
    password=os.getenv("FRITZ_PASSWORD")
)
print(fc)  # print router model information

# Get messages from the telephone answering machine (TAM)
tam = FritzTAM(fc=fc)

# Get list of TAMs
print("\nTAM List:")
print(tam.tam_list())

# Get messages from the default TAM (index 0)
print("\nMessages from TAM:")
messages = tam.message_list(tamIndex="0")
for i, message in enumerate(messages):
    print(f"{i}: {message}")

def play_message(tam, tam_index="0", message_index=None):
    """Download and play a TAM message."""
    try:
        print(f"\nDownloading message {message_index}...")
        message_data = tam.message(tamIndex=tam_index, messageIndex=message_index)
        
        # Create temporary file for the message
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(message_data)
            temp_path = temp_file.name
        
        print(f"Playing message from {temp_path}...")
        
        # Play the audio based on platform
        if sys.platform == "win32":
            winsound.PlaySound(temp_path, winsound.SND_FILENAME)
        elif sys.platform == "darwin":
            subprocess.run(["afplay", temp_path], check=True)
        else:  # Linux
            subprocess.run(["aplay", temp_path], check=True)
        
        print("Playback complete!")
        # Clean up
        Path(temp_path).unlink()
        
    except Exception as e:
        print(f"Error playing message: {e}")

# Interactive menu to play messages
if messages:
    while True:
        print("\n--- Message Playback Menu ---")
        for i, message in enumerate(messages):
            called = message.get("Called", "Unknown")
            date = message.get("Date", "Unknown")
            print(f"  {i}: From {called} on {date}")
        
        print(f"  {len(messages)}: Exit")
        
        try:
            choice = input("\nEnter message number to play: ").strip()
            choice_num = int(choice)
            
            if choice_num == len(messages):
                print("Goodbye!")
                break
            
            if 0 <= choice_num < len(messages):
                message_index = messages[choice_num].get("Index")
                play_message(tam, tam_index="0", message_index=message_index)
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
else:
    print("No messages found.")