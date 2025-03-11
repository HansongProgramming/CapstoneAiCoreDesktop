
<img src="https://github.com/HansongProgramming/CapstoneAiCoreDesktop/blob/main/images/AiCore-Cre8TiveSync.png](https://github.com/HansongProgramming/CapstoneAiCoreDesktop/blob/main/images/AiCore-Cre8tiveSync.png">

Flores Hans Harold L.
Reburiano Augnina Krizel P.
  


# AiCore: Artificial Intelligence for Crimescene Observation and Reconstruction Enhancement.

AiCore is an AI-driven tool designed for bloodstain pattern analysis to automate calculations, crime scene reconstruction, and report generation. 
It leverages advanced 3D plotting, simulation, and computer vision technologies to assist forensic investigators in reconstructing crime scenes efficiently.

---

## Features

- **3D Bloodstain Pattern Visualization:**
  - Utilizes `PyVista` for detailed 3D plotting of bloodstain patterns.
    
- **Spatter Calculation:**
  - Employs Meta's `Segment Anything` model to identify and calculate blood spatter patterns with precision.

- **Advanced AI Integration:**
  - Built on `OpenCV`, `PyTorch`, and `NumPy` for image processing and deep learning-based pattern recognition.

- **Data Visualization:**
  - Includes `Matplotlib` for clear, customizable 2D visualizations.

- **Automated Report Generation:**
  - Creates detailed forensic reports with analysis summaries, visualizations, and key findings.

---
  
<h2>💻 Built with</h2>
Technologies used in the project:

*   Pyvista
*   Pyqt
*   OpenCV
*   Matplotlib
*   Segment-Anything
*   Pillow
*   PyTorch
*   OS
*   SYS
*   Json
*   Python-Docx
*   numpy

## Technologies Used

| Library/Framework | Purpose |
|--------------------|---------|
| **PyVista**        | 3D plotting and visualization of bloodstain patterns. |
| **Segment Anything** | AI model for spatter segmentation and calculation. |
| **OpenCV**         | Image processing for crime scene analysis. |
| **PyTorch**        | Deep learning for pattern recognition and classification. |
| **NumPy**          | Numerical calculations and matrix operations. |
| **Matplotlib**     | Data visualization and plotting of results. |
|**pillow** | image manipulation and processing|
| **os** | for operating system commands |
|**python-docx**| to export and generate responses|
|**pyqt** | for system GUI|
|**pyvistaqt** | to use QtInteractor as the plotter / simulation|
---

## Installation

To get started with AICore, follow these steps:

1. **Download the Setup.exe from the release**

2. **Run the Setup.exe**

3. **Select Installation Directory**

4. **Start the installation**
---

## Usage
1. **Run AICore**
   using AiCore.exe

2. **Input Crime Scene Data**
   - Provide images of the crime scene for analysis.
   - You can import images through pressing Add Floor / any of the walls.

3. **View 3D Visualizations**
   - Access the generated 3D models and patterns via the PyVista interface.

4. **Generate Reports**
   - Automatically creates forensic reports with single button press

---

## Example Workflow

1. Upload high-resolution images of the bloodstain patterns from the crime scene.
2. Select Blood spatters by Pressing Add Points
3. Wait as the system analyzes the stains for you!
4. You can press add head to see where the expected Area of convergence is.
5. The Export(2d view) buttons saves an image of the image with the layers of analysis.
6. The Export(3d view) buttons saves the plotter as a png image including all actors and scene.

### Theme and customization
1. Light mode is added inside edit > switch to light mode
2. Alternatively, dark mode is inside edit > switch to dark mode when light mode is toggled.
---

## Contributions

Contributions are welcome! If you'd like to contribute to AICore, please follow these steps:

1. Fork the repository.
2. Create a new branch.
   ```bash
   git checkout -b feature-branch-name
   ```
3. Commit your changes.
   ```bash
   git commit -m "Add your message here"
   ```
4. Push to your branch.
   ```bash
   git push origin feature-branch-name
   ```
5. Submit a pull request.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

---

## Contact

For questions or support, feel free to contact:
- **HansongProgramming**: [hlf1850@students.uc-bcf.edu.ph](mailto:hlf1850@students.uc-bcf.edu.ph)
- GitHub: [github.com/HansongProgramming](https://github.com/HansongProgramming)

- **Augnina**: [apr1299@students.uc-bcf.edu.ph](mailto:apr1299@students.uc-bcf.edu.ph)
- GitHub: [github.com/Augnina](https://github.com/Augnina)
---

## Acknowledgments

- **PyVista** for 3D plotting.
- **Segment Anything** by Meta for spatter segmentation.
- **University of the Cordilleras - College of Information Technology and Computer Science**
- **Wangal Regional Forensics Unit** by providing feedback.
- **SpatterSense Thesis - UC-Forensics** for supporting the development.
- The open-source community for making these technologies accessible.

---

**Cre8Tive Sync** hopes AiCore can assist forensic teams in solving crimes faster and more accurately! 


