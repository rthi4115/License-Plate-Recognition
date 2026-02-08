# Import required libraries
import cv2                  # OpenCV for image processing
import numpy as np           # Numerical operations
import pytesseract           # OCR (Optical Character Recognition)
import re                    # Regular expressions for text cleaning


# ---------- OPTIONAL: Configure Tesseract path ----------
# If Tesseract is already installed and added to PATH, you DON'T need this.
# Uncomment ONLY if Python cannot find tesseract automatically.

# Windows example:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class RobustLicensePlateRecognizer:
    def __init__(self):
        """
        Constructor:
        - OCR configuration
        - CLAHE object for contrast enhancement
        """
        # OCR configuration:
        # --oem 3 : Default OCR engine
        # --psm 7 : Treat image as a single line of text
        # whitelist : Allow only capital letters and numbers
        self.custom_config = (
            r'--oem 3 --psm 7 '
            r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        )

        # CLAHE improves contrast in low-light or shadow areas
        self.clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))


    def get_contours(self, img):
        """
        Preprocess image and extract contours
        """
        # Convert image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE to improve contrast
        gray = self.clahe.apply(gray)

        # Bilateral filter reduces noise but keeps edges sharp
        blur = cv2.bilateralFilter(gray, 11, 17, 17)

        # Adaptive threshold handles uneven lighting
        thresh = cv2.adaptiveThreshold(
            blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

        # Canny edge detection finds strong edges
        edged = cv2.Canny(blur, 30, 200)

        # Combine threshold + edge detection
        combined = cv2.bitwise_or(thresh, edged)

        # Find contours in the processed image
        cnts, _ = cv2.findContours(
            combined.copy(),
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Return largest contours first + grayscale image
        return sorted(cnts, key=cv2.contourArea, reverse=True)[:30], gray


    def process_image(self, img):
        """
        Detect license plate regions and extract text
        """
        contours, gray = self.get_contours(img)
        results = []

        for c in contours:
            # Ignore very small contours (noise)
            area = cv2.contourArea(c)
            if area < 300:
                continue

            # Approximate contour shape
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            # License plates usually have 4–8 corners
            if 4 <= len(approx) <= 8:
                x, y, w, h = cv2.boundingRect(c)

                # Width-to-height ratio check
                aspect_ratio = w / float(h)
                if 1.5 <= aspect_ratio <= 8.0:

                    # Extract region of interest (ROI)
                    roi = gray[y:y+h, x:x+w]
                    if roi.size == 0:
                        continue

                    # Enlarge ROI for better OCR accuracy
                    roi = cv2.resize(
                        roi, None,
                        fx=3, fy=3,
                        interpolation=cv2.INTER_CUBIC
                    )

                    # Convert ROI to binary image
                    _, roi_thresh = cv2.threshold(
                        roi, 0, 255,
                        cv2.THRESH_BINARY + cv2.THRESH_OTSU
                    )

                    # Extract text using Tesseract OCR
                    text = pytesseract.image_to_string(
                        roi_thresh,
                        config=self.custom_config
                    ).strip()

                    # Remove unwanted characters
                    clean_text = re.sub(
                        r'[^A-Z0-9]', '',
                        text.upper()
                    )

                    # Store valid plate numbers
                    if len(clean_text) >= 4:
                        results.append({
                            'bbox': (x, y, w, h),
                            'text': clean_text
                        })

        # Remove duplicate detections
        seen = set()
        unique_results = []
        for r in results:
            if r['text'] not in seen:
                unique_results.append(r)
                seen.add(r['text'])

        return unique_results


    def draw_results(self, img, results):
        """
        Draw bounding boxes and detected text on image
        """
        for r in results:
            x, y, w, h = r['bbox']

            # Draw rectangle around license plate
            cv2.rectangle(
                img, (x, y),
                (x + w, y + h),
                (0, 255, 0), 2
            )

            # Display recognized text
            cv2.putText(
                img, r['text'],
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 255, 0), 2
            )
        return img


# ---------- MAIN PROGRAM ----------
if __name__ == "__main__":

    print("="*60)
    print("🚗 LICENSE PLATE RECOGNITION - REAL-TIME DETECTION")
    print("="*60)
    print("\n📸 Opening camera...")
    print("Press 'q' to quit\n")

    # Create recognizer object
    recognizer = RobustLicensePlateRecognizer()

    # Open camera (0 = default camera)
    cap = cv2.VideoCapture(0)

    # Try alternative camera index if default fails
    if not cap.isOpened():
        print("⚠ Trying alternative camera index...")
        cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("❌ ERROR: Cannot access camera!")
        print("\n✓ SOLUTIONS:")
        print("  1. Check if camera is connected")
        print("  2. Check camera permissions")
        print("  3. Close other apps using camera")
        print("  4. Try restarting the application")
        print("  5. On Linux: sudo chmod 666 /dev/video*")
        exit(1)

    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    print(f"✓ Camera opened: {frame_width}x{frame_height} @ {fps}fps")
    print("\n" + "="*60)
    print("Waiting for license plates...")
    print("="*60 + "\n")

    frame_count = 0
    detected_plates = {}
    last_detected_plate = None

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("❌ Failed to read frame from camera")
                break

            frame_count += 1
            display_frame = frame.copy()

            # Process frame for license plates
            results = recognizer.process_image(frame)

            # Draw rectangles on main frame
            display_frame = recognizer.draw_results(display_frame, results)

            # If license plate detected
            if results:
                for r in results:
                    x, y, w, h = r['bbox']
                    plate_text = r['text']
                    
                    # Track detected plates
                    if plate_text != last_detected_plate:
                        detected_plates[plate_text] = detected_plates.get(plate_text, 0) + 1
                        last_detected_plate = plate_text

                        # Print detection
                        print(f"\n{'🎯 DETECTED PLATE':-^60}")
                        print(f"License Plate: {plate_text}")
                        print(f"Frame: {frame_count}")
                        print("-"*60)

                        # Extract plate region in grayscale
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        plate_region = gray[y:y+h, x:x+w]

                        if plate_region.size > 0:
                            # Upscale plate for better visibility
                            plate_enlarged = cv2.resize(
                                plate_region, None, 
                                fx=4, fy=4, 
                                interpolation=cv2.INTER_CUBIC
                            )

                            # Add border and text
                            plate_with_text = cv2.copyMakeBorder(
                                plate_enlarged, 40, 40, 10, 10, 
                                cv2.BORDER_CONSTANT, value=255
                            )
                            cv2.putText(
                                plate_with_text,
                                f"PLATE: {plate_text}",
                                (15, 25),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.2,
                                (0, 255, 0),
                                3
                            )

                            # Save this detection
                            save_name = f"plate_detected_{plate_text}_{frame_count}.jpg"
                            cv2.imwrite(save_name, plate_with_text)
                            print(f"Saved: {save_name}")

                            # Display in popup
                            cv2.imshow("📋 DETECTED LICENSE PLATE (GRAYSCALE)", plate_with_text)

            # Add info text on main feed
            cv2.putText(
                display_frame,
                f"Frame: {frame_count} | Plates: {len(detected_plates)} unique",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            # Show main camera feed
            cv2.imshow("📹 CAMERA FEED - License Plate Detection", display_frame)

            # Press 'q' to quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n⏹ Stopping detection...")
                break

    except KeyboardInterrupt:
        print("\n⏹ Interrupted by user")
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()

        # Final summary
        print("\n" + "="*60)
        print("📊 SESSION SUMMARY")
        print("="*60)
        print(f"Total frames processed: {frame_count}")
        if detected_plates:
            print(f"Unique plates detected: {len(detected_plates)}")
            for plate, count in sorted(detected_plates.items()):
                print(f"  • {plate}: {count} detection(s)")
        else:
            print("No license plates detected in this session.")
        print("="*60 + "\n")

    # Get camera properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    print(f"Camera opened successfully: {frame_width}x{frame_height} @ {fps}fps\n")

    frame_count = 0
    detected_plates = {}

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Error: Failed to read frame from camera")
                break

            frame_count += 1

            # Process frame for license plates
            results = recognizer.process_image(frame)

            # Draw detected plates with green rectangles
            display_frame = frame.copy()
            display_frame = recognizer.draw_results(display_frame, results)

            # If plates detected, extract and display grayscale plate image
            if results:
                for i, r in enumerate(results):
                    x, y, w, h = r['bbox']
                    plate_text = r['text']
                    detected_plates[plate_text] = detected_plates.get(plate_text, 0) + 1

                    # Extract the plate region from grayscale image
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    plate_region = gray[y:y+h, x:x+w]

                    # Create a grayscale image with the plate text displayed
                    if plate_region.size > 0:
                        # Upscale for better visibility
                        plate_display = cv2.resize(plate_region, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

                        # Convert to 3-channel to add text
                        plate_display_3ch = cv2.cvtColor(plate_display, cv2.COLOR_GRAY2BGR)

                        # Add text on top
                        cv2.putText(
                            plate_display_3ch,
                            f"Plate: {plate_text}",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            2
                        )

                        # Display the grayscale plate image
                        cv2.imshow("Detected License Plate (Grayscale)", plate_display_3ch)

                        # Print detection info
                        print(f"[Frame {frame_count}] Detected: {plate_text}")

                        # Save the grayscale plate image
                        output_filename = f"plate_{plate_text}_{frame_count}.jpg"
                        cv2.imwrite(output_filename, plate_display)

            # Display main camera feed with detections
            cv2.imshow("License Plate Detection (Live)", display_frame)

            # Press 'q' to quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()

        # Print summary
        print("\n" + "="*50)
        print("Detection Summary:")
        print("="*50)
        if detected_plates:
            for plate, count in detected_plates.items():
                print(f"  {plate}: detected {count} time(s)")
            print(f"\nTotal unique plates: {len(detected_plates)}")
        else:
            print("No license plates detected during the session.")
        print("="*50)
