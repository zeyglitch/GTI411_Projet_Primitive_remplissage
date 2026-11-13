import cv2
import numpy as np




def record_video():
    cap = cv2.VideoCapture(0)

    # Check if webcam opened successfully
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    # Get webcam properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 20.0

    # Create filename with timestamp
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f'webcam_video.avi'

    # Define codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_filename, fourcc, fps, (frame_width, frame_height))

    print("Controls:")
    print("- Recording started automatically")
    print("- Q or ESC: Stop recording and quit")
    print(f"- Saving to: {output_filename}")

    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to capture frame")
            break
        
        # Write frame to video file
        out.write(frame)
        
        # Display the frame with recording indicator
        cv2.putText(frame, 'REC', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow('Webcam Recording', frame)
        
        # Q or ESC to stop recording
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print(f"Recording saved as: {output_filename}")



# On reutilise exactement la classe BackgroundRemover de la partie 3 (dossier GTI411-Lab3)
import os, sys
DOSSIER_LAB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "GTI411-Lab3")
sys.path.insert(0, DOSSIER_LAB)
from part3_background_remover import BackgroundRemover


def charger_image_rgb(path):
    image = cv2.imread(path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)



def main():
    video_path = 'webcam_video.avi'  # Replace with your video file path
    cap = cv2.VideoCapture(video_path)

    remover = BackgroundRemover()
    remover.set_background_image(charger_image_rgb("background_image.png"))
    remover.set_replacement_image(charger_image_rgb(os.path.join(DOSSIER_LAB, "images", "fond_remplacement.jpg")))

    # Load background image

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    delay = int(1000 / fps)  # Delay in milliseconds between frames

    paused = False

    print("Controls:")
    print("- SPACE: Play/Pause")
    print("- Q or ESC: Quit")
    print("- R toogle between blur and replace")

    while True:
        if not paused:
            ret, frame = cap.read()
            
            # If frame reading was not successful, end of video
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = remover.remove_background(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Display the frame
            cv2.imshow('Video Player', frame)
        
        # Wait for key press
        key = cv2.waitKey(delay if not paused else 1) & 0xFF
        
        # Spacebar to toggle play/pause
        if key == ord(' '):
            paused = not paused
            print("Paused" if paused else "Playing")
        
        # Q or ESC to quit
        elif key == ord('q') or key == 27:
            break

        elif key == ord('r'):
            remover.set_modify_effect("replace" if remover.modify_effect == "blur" else "blur")
            print(f"Switching to {remover.modify_effect}")


    # Release resources
    cap.release()
    cv2.destroyAllWindows()




if __name__ == "__main__":
    # record_video()
    main()