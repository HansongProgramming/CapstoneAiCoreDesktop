from imports import *

class AnalysisThread(QThread):
    progress_updated = pyqtSignal(int)
    analysis_done = pyqtSignal(list)
    mask_ready = pyqtSignal(object, object)  

    def __init__(self, segment_map_instance, selection_boxes, predictor, image_np, device):
        super().__init__()
        self.segment_map = segment_map_instance  
        self.selection_boxes = selection_boxes
        self.predictor = predictor
        self.image_np = image_np
        self.device = device

    def run(self):
        """Runs the selection analysis in a separate thread."""
        try:
            self.predictor.set_image(self.image_np)
            results = []

            for i, box in enumerate(self.selection_boxes):
                input_box = np.array([box['x1'], box['y1'], box['x2'], box['y2']])
                input_box = torch.tensor(input_box, device=self.device)

                masks, _, _ = self.predictor.predict(
                    box=input_box[None, :].cpu().numpy(), 
                    multimask_output=False
                )

                if masks is not None and len(masks) > 0:
                    self.mask_ready.emit(masks[0], i)
                    
                    impact_angle, segment_data = self.segment_map.process_spatter(masks[0])
                    results.append(segment_data)

                self.progress_updated.emit(int((i + 1) / len(self.selection_boxes) * 100))

            self.analysis_done.emit(results)

        except Exception as e:
            QMessageBox.warning(self, "Error",f"Error in analysis thread: {e}")