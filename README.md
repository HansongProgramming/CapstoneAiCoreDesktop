
<img src="https://github.com/HansongProgramming/CapstoneAiCoreDesktop/blob/main/images/aicore.png">
<p id="description">Artificial Intelligence in Crime Observations and Reconstruction Efficiency</p>


Developed By:
<img src="https://github.com/HansongProgramming/CapstoneAiCoreDesktop/blob/main/images/Cre8Tive%20Sync.png">
Flores Hans Harold L.
Reburiano Augnina Krizel P.
  


# AICore: AI for Bloodstain Pattern Analysis (BPA)

AICore is a cutting-edge AI-driven tool designed for bloodstain pattern analysis to automate calculations, crime scene recognition, and report generation. It leverages advanced 3D plotting, simulation, and AI technologies to assist forensic investigators in reconstructing crime scenes efficiently and accurately.

---

## Features

- **3D Bloodstain Pattern Visualization:**
  - Utilizes `PyVista` for detailed 3D plotting of bloodstain patterns.

- **Simulation Tools:**
  - Powered by Blender's Python API to simulate and analyze spatter patterns in crime scenes.

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
| **Blender Python** | Simulation and modeling of spatter patterns in 3D environments. |
| **Segment Anything** | AI model for spatter segmentation and calculation. |
| **OpenCV**         | Image processing for crime scene analysis. |
| **PyTorch**        | Deep learning for pattern recognition and classification. |
| **NumPy**          | Numerical calculations and matrix operations. |
| **Matplotlib**     | Data visualization and plotting of results. |
|**pillow** | image manipulation and processing|
| **os** | for operating system commands |
|**python-docx**| to export and generate responses|
|**pyqt** | for system GUI|
---

## Installation

To get started with AICore, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/AICore.git
   cd AICore
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Blender Python API**
   - Ensure Blender is installed ([Download Blender](https://www.blender.org/download/)).
   - Add the Blender Python API to your environment. Refer to Blender's [official documentation](https://docs.blender.org/api/current/) for setup instructions.

---

## Usage

1. **Input Crime Scene Data**
   - Provide images or videos of the crime scene for analysis.

2. **Run AICore**
   ```bash
   python main.py --input path_to_data
   ```

3. **View 3D Visualizations**
   - Access the generated 3D models and patterns via the PyVista interface.

4. **Generate Reports**
   - Automatically creates forensic reports with a single command:
     ```bash
     python generate_report.py --output report.pdf
     ```

---

## Example Workflow

1. Upload high-resolution images of the bloodstain patterns from the crime scene.
2. Run the simulation in Blender to recreate the pattern's trajectories.
3. Use AICore’s AI algorithms to segment, classify, and calculate blood spatter details.
4. Visualize the findings in 3D.
5. Generate a detailed report summarizing the findings, including visuals and key calculations.

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or support, feel free to contact:
- **Your Name**: [your.email@example.com](mailto:your.email@example.com)
- GitHub: [github.com/yourusername](https://github.com/yourusername)

---

## Acknowledgments

- **PyVista** for 3D plotting.
- **Blender** for simulation capabilities.
- **Segment Anything** by Meta for spatter segmentation.
- The open-source community for making these technologies accessible.

---

We hope AICore can assist forensic teams in solving crimes faster and more accurately!


