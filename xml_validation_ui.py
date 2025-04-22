
#!/usr/bin/env python3
"""
Compact XML Question Validation Tool

A lightweight validation tool for XML question data with all UI elements on a single screen.
Automatically saves progress when moving between questions or exiting.
Updated to use a 6-checkbox checklist with tooltip colors matching UI theme, tooltips positioned
to the left of checkboxes, and JSON output explicitly storing percentage of each checkbox checked.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import xml.etree.ElementTree as ET
import json
from datetime import datetime

class Tooltip:
    """Create a tooltip for a Tkinter widget"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        # Position tooltip to the left of the checkbox
        tooltip_width = 200  # Estimated width based on wraplength
        x = self.widget.winfo_rootx() - tooltip_width - 10  # 10px gap to the left
        y = self.widget.winfo_rooty()  # Align top with checkbox
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            background="#d9d9d9",  # Matches Tkinter default UI background
            foreground="#000000",  # Black text for contrast
            relief="solid",
            borderwidth=1,
            bd=1,
            highlightbackground="#000000",  # Black border
            wraplength=200
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class CompactXMLValidator:
    def __init__(self, root, xml_file=None):
        self.root = root
        self.root.title("XML Question Validator")
        self.root.geometry("1000x700")
        
        # Application state
        self.segments = []
        self.current_index = 0
        self.checklist = {}  # Stores checklist states {question_id: {criterion: bool}}
        self.comments = {}
        
        # Create main UI
        self.create_ui()
        
        # Load XML file if provided
        if xml_file:
            self.load_xml(xml_file)
            
        # Set up auto-save on exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Menu bar
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open XML...", command=self.open_file)
        file_menu.add_command(label="View Summary Stats", command=self.show_summary)
        file_menu.add_command(label="Export JSON...", command=self.export_json)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)
        
        # Top frame for navigation
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        # Navigation buttons
        self.prev_btn = ttk.Button(top_frame, text="← Previous", command=self.prev_question)
        self.prev_btn.pack(side=tk.LEFT)
        
        self.position_label = ttk.Label(top_frame, text="Question 0 of 0")
        self.position_label.pack(side=tk.LEFT, padx=20)
        
        self.next_btn = ttk.Button(top_frame, text="Next →", command=self.next_question)
        self.next_btn.pack(side=tk.RIGHT)
        
        # Progress bar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left side - question info
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Segment text
        segment_frame = ttk.LabelFrame(left_frame, text="Segment Text")
        segment_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.segment_text = scrolledtext.ScrolledText(segment_frame, wrap=tk.WORD, height=8, font=("TkDefaultFont", 12))
        self.segment_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Question text
        question_frame = ttk.LabelFrame(left_frame, text="Question")
        question_frame.pack(fill=tk.X, pady=5)
        
        self.question_text = scrolledtext.ScrolledText(question_frame, wrap=tk.WORD, height=4, font=("TkDefaultFont", 12))
        self.question_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Choices
        choices_frame = ttk.LabelFrame(left_frame, text="Choices")
        choices_frame.pack(fill=tk.X, pady=5)
        
        self.choices_container = ttk.Frame(choices_frame)
        self.choices_container.pack(fill=tk.X, padx=5, pady=5)
        
        # Right side - validation
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Checklist frame
        checklist_frame = ttk.LabelFrame(right_frame, text="Reasoning Quality Checklist")
        checklist_frame.pack(fill=tk.X, pady=5)
        
        # Checklist variables
        self.checklist_vars = {
            "single_sentence": tk.BooleanVar(value=False),
            "multiple_sentences": tk.BooleanVar(value=False),
            "low_quality_distractors": tk.BooleanVar(value=False),
            "unsuitable_paragraph": tk.BooleanVar(value=False),
            "unclear_answer": tk.BooleanVar(value=False),
            "outside_knowledge": tk.BooleanVar(value=False)
        }
        
        # Checklist checkboxes with tooltips
        checklist_items = [
            ("Cần một câu", "single_sentence", "Đánh dấu nếu câu hỏi chỉ cần thông tin từ một câu trong đoạn văn để trả lời."),
            ("Cần nhiều câu", "multiple_sentences", "Đánh dấu nếu câu hỏi cần thông tin từ nhiều câu trong đoạn văn để trả lời."),
            ("Lựa chọn sai kém chất lượng", "low_quality_distractors", "Đánh dấu nếu các lựa chọn sai không liên quan đến đoạn văn hoặc quá dễ loại bỏ, làm đáp án đúng quá rõ ràng."),
            ("Đoạn văn không phù hợp", "unsuitable_paragraph", "Đánh dấu nếu đoạn văn quá nhạy cảm, liên quan đến chính trị, hoặc không phù hợp để đặt câu hỏi."),
            ("Đáp án không rõ ràng", "unclear_answer", "Đánh dấu nếu câu hỏi có nhiều đáp án đúng hoặc đáp án đúng không rõ ràng dựa trên đoạn văn."),
            ("Cần kiến thức ngoài", "outside_knowledge", "Đánh dấu nếu câu hỏi hoặc đáp án cần kiến thức bên ngoài đoạn văn để trả lời.")
        ]
        
        for label, var_key, tooltip in checklist_items:
            cb_frame = ttk.Frame(checklist_frame)
            cb_frame.pack(fill=tk.X, pady=2)
            cb = ttk.Checkbutton(cb_frame, text=label, variable=self.checklist_vars[var_key], command=self.save_current_checklist)
            cb.pack(side=tk.LEFT)
            Tooltip(cb, tooltip)
        
        # Comments frame
        comments_frame = ttk.LabelFrame(right_frame, text="Comments")
        comments_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.comments_text = scrolledtext.ScrolledText(comments_frame, wrap=tk.WORD)
        self.comments_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind event to save comment
        self.comments_text.bind("<KeyRelease>", self.save_current_comment)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.save_indicator = ttk.Label(status_frame, text="")
        self.save_indicator.pack(side=tk.RIGHT)
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open XML File",
            filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")]
        )
        if file_path:
            self.load_xml(file_path)
    
    def load_xml(self, file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            self.xml_file_path = file_path
            self.segments = []
            
            for segment in root.findall("Segment"):
                segment_id = segment.get("id")
                segment_text = segment.find("SegmentText")
                if segment_text is None or not segment_text.text:
                    continue
                
                doc_title = segment.find("DocumentTitle")
                doc_title_text = doc_title.text if doc_title is not None else "Unknown"
                
                segment_title = segment.find("SegmentTitle")
                segment_title_text = segment_title.text if segment_title is not None else ""
                
                qa_elem = segment.find("QA")
                if qa_elem is None:
                    continue
                
                for question_elem in qa_elem.findall("Question"):
                    question_id = question_elem.get("id")
                    question_type_elem = question_elem.find("QuestionType")
                    question_type = question_type_elem.text if question_type_elem is not None else ""
                    question_text_elem = question_elem.find("QuestionText")
                    if question_text_elem is None or not question_text_elem.text:
                        continue
                    
                    choices_elem = question_elem.find("Choices")
                    if choices_elem is None:
                        continue
                    
                    choices = []
                    for choice_elem in choices_elem.findall("Choice"):
                        choice_id = choice_elem.get("id")
                        if choice_elem.text:
                            choices.append({"id": choice_id, "text": choice_elem.text})
                    
                    correct_choice_elem = question_elem.find("CorrectChoice")
                    correct_choice = correct_choice_elem.text if correct_choice_elem is not None else ""
                    
                    self.segments.append({
                        "segment_id": segment_id,
                        "document_title": doc_title_text,
                        "segment_title": segment_title_text,
                        "segment_text": segment_text.text,
                        "question_id": question_id,
                        "question_type": question_type,
                        "question_text": question_text_elem.text,
                        "choices": choices,
                        "correct_choice": correct_choice
                    })
            
            if self.segments:
                print(f"Successfully loaded {len(self.segments)} questions")
                self.status_label.config(text=f"Loaded {len(self.segments)} questions from {os.path.basename(file_path)}")
                self.try_load_progress()
                self.update_progress_bar()
                self.root.title(f"Question Validator - {os.path.basename(file_path)}")
            else:
                messagebox.showwarning("No Data", "No valid questions found in the XML file.")
                self.status_label.config(text="No valid questions found in the XML file")
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load XML file: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
    
    def load_question(self, index):
        if not self.segments or index < 0 or index >= len(self.segments):
            return
        
        self.auto_save_progress()
        data = self.segments[index]
        self.current_index = index
        
        self.segment_text.config(state=tk.NORMAL)
        self.segment_text.delete(1.0, tk.END)
        self.segment_text.insert(tk.END, data["segment_text"])
        self.segment_text.config(state=tk.DISABLED)
        
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        question_header = f"({data['question_type']}) "
        self.question_text.insert(tk.END, question_header, "bold")
        self.question_text.insert(tk.END, data["question_text"])
        self.question_text.tag_configure("bold", font=("TkDefaultFont", 12, "bold"))
        self.question_text.config(state=tk.DISABLED)
        
        for widget in self.choices_container.winfo_children():
            widget.destroy()
        
        for i, choice in enumerate(data["choices"]):
            is_correct = choice["id"] == data["correct_choice"]
            choice_frame = ttk.Frame(self.choices_container)
            choice_frame.pack(fill=tk.X, pady=2)
            
            if is_correct:
                choice_label = tk.Label(
                    choice_frame, 
                    text=choice['text'], 
                    anchor="w",
                    wraplength=350,
                    justify=tk.LEFT
                )
                choice_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                check_label = tk.Label(
                    choice_frame, 
                    text="✓", 
                    fg="red",
                    font=("TkDefaultFont", 12, "bold")
                )
                check_label.pack(side=tk.RIGHT, padx=5)
            else:
                choice_label = tk.Label(
                    choice_frame, 
                    text=choice['text'], 
                    anchor="w",
                    wraplength=350,
                    justify=tk.LEFT
                )
                choice_label.pack(fill=tk.X, padx=5)
        
        self.position_label.config(text=f"Question {index + 1} of {len(self.segments)}")
        self.prev_btn.config(state=tk.NORMAL if index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if index < len(self.segments) - 1 else tk.DISABLED)
        
        question_id = data["question_id"]
        checklist_state = self.checklist.get(question_id, {
            "single_sentence": False,
            "multiple_sentences": False,
            "low_quality_distractors": False,
            "unsuitable_paragraph": False,
            "unclear_answer": False,
            "outside_knowledge": False
        })
        for key, var in self.checklist_vars.items():
            var.set(checklist_state[key])
        
        self.comments_text.delete(1.0, tk.END)
        if question_id in self.comments:
            self.comments_text.insert(tk.END, self.comments[question_id])
        
        self.update_progress_bar()
    
    def prev_question(self):
        if self.current_index > 0:
            self.load_question(self.current_index - 1)
    
    def next_question(self):
        if self.current_index < len(self.segments) - 1:
            self.load_question(self.current_index + 1)
    
    def save_current_checklist(self):
        if not self.segments:
            return
            
        question_id = self.segments[self.current_index]["question_id"]
        checklist_state = {key: var.get() for key, var in self.checklist_vars.items()}
        self.checklist[question_id] = checklist_state
        self.update_progress_bar()
        self.show_save_indicator()
    
    def save_current_comment(self, event=None):
        if not self.segments:
            return
            
        question_id = self.segments[self.current_index]["question_id"]
        comment = self.comments_text.get(1.0, tk.END).strip()
        self.comments[question_id] = comment
        self.show_save_indicator()
    
    def update_progress_bar(self):
        if not self.segments:
            self.progress_bar["value"] = 0
            return
        
        # Count questions with at least one checklist item checked
        checked_count = sum(1 for qid in [s["question_id"] for s in self.segments] 
                          if qid in self.checklist and any(self.checklist[qid].values()))
        progress_value = (checked_count / len(self.segments)) * 100
        self.progress_bar["value"] = progress_value
    
    def auto_save_progress(self):
        if not hasattr(self, 'xml_file_path') or not self.segments:
            return
        self.save_progress(silent=True)
    
    def save_progress(self, silent=False):
        if not hasattr(self, 'xml_file_path'):
            if not silent:
                messagebox.showinfo("No File", "Please open an XML file first.")
            return
        
        # Calculate summary stats for metadata
        total_questions = len(self.segments)
        checked_questions = sum(1 for qid in [s["question_id"] for s in self.segments] 
                            if qid in self.checklist and any(self.checklist[qid].values()))
        
        # Calculate counts and percentages for each checkbox
        counts = {
            "single_sentence": 0,
            "multiple_sentences": 0,
            "low_quality_distractors": 0,
            "unsuitable_paragraph": 0,
            "unclear_answer": 0,
            "outside_knowledge": 0
        }
        for qid in [s["question_id"] for s in self.segments]:
            if qid in self.checklist:
                for criterion, checked in self.checklist[qid].items():
                    if checked:
                        counts[criterion] += 1
        
        progress_data = {
            "timestamp": datetime.now().isoformat(),
            "checklist": self.checklist,
            "comments": self.comments,
            "current_index": self.current_index,
            "metadata": {
                "total_questions": total_questions,
                "questions_checked": checked_questions,
                "completion_percentage": round((checked_questions / total_questions) * 100, 1) if total_questions else 0,
                "checklist_percentages": {
                    criterion: round(count / total_questions * 100, 2) if total_questions else 0
                    for criterion, count in counts.items()
                }
            }
        }
        
        try:
            base_name = os.path.splitext(self.xml_file_path)[0]
            progress_file = f"{base_name}_progress.json"
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
            
            if not silent:
                messagebox.showinfo("Success", f"Progress saved to:\n{progress_file}")
            return True
        except Exception as e:
            if not silent:
                messagebox.showerror("Error", f"Failed to save progress: {str(e)}")
            return False

    def show_save_indicator(self):
        self.save_indicator.config(text="Saving...")
        self.root.after(1000, self.auto_save_progress)
        self.root.after(1500, lambda: self.save_indicator.config(text="Saved"))
        self.root.after(3000, lambda: self.save_indicator.config(text=""))
    
    def try_load_progress(self):
        if not hasattr(self, 'xml_file_path'):
            return
        
        base_name = os.path.splitext(self.xml_file_path)[0]
        progress_file = f"{base_name}_progress.json"
        
        if not os.path.exists(progress_file):
            self.load_question(0)
            return
        
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "checklist" in data:
                self.checklist = data["checklist"]
            
            if "comments" in data:
                self.comments = data["comments"]
            
            if "current_index" in data:
                current_idx = data["current_index"]
                if 0 <= current_idx < len(self.segments):
                    self.load_question(current_idx)
                else:
                    self.load_question(0)
            else:
                self.load_question(0)
            
            if "metadata" in data and "completion_percentage" in data["metadata"]:
                completed = data["metadata"]["completion_percentage"]
                self.status_label.config(text=f"Loaded previous progress. Completion: {completed}%")
            else:
                self.status_label.config(text=f"Loaded previous progress from {os.path.basename(progress_file)}")
        except Exception as e:
            print(f"Failed to load progress: {str(e)}")
            self.load_question(0)
    
    def show_summary(self):
        if not self.segments:
            messagebox.showinfo("No Data", "No questions loaded yet.")
            return
        
        total_questions = len(self.segments)
        checked_questions = sum(1 for qid in [s["question_id"] for s in self.segments] 
                               if qid in self.checklist and any(self.checklist[qid].values()))
        commented_questions = sum(1 for qid in [s["question_id"] for s in self.segments] 
                                 if qid in self.comments and self.comments[qid])
        
        counts = {
            "single_sentence": 0,
            "multiple_sentences": 0,
            "low_quality_distractors": 0,
            "unsuitable_paragraph": 0,
            "unclear_answer": 0,
            "outside_knowledge": 0
        }
        for qid in [s["question_id"] for s in self.segments]:
            if qid in self.checklist:
                for criterion, checked in self.checklist[qid].items():
                    if checked:
                        counts[criterion] += 1
        
        msg = "VALIDATION SUMMARY\n\n"
        msg += f"Total questions: {total_questions}\n"
        msg += f"Questions checked: {checked_questions} ({checked_questions/total_questions*100:.1f}%)\n"
        msg += f"Questions with comments: {commented_questions}\n\n"
        msg += "Checklist percentages:\n"
        for criterion, count in counts.items():
            percentage = count / total_questions * 100 if total_questions > 0 else 0
            label = {
                "single_sentence": "Cần một câu",
                "multiple_sentences": "Cần nhiều câu",
                "low_quality_distractors": "Lựa chọn sai kém chất lượng",
                "unsuitable_paragraph": "Đoạn văn không phù hợp",
                "unclear_answer": "Đáp án không rõ ràng",
                "outside_knowledge": "Cần kiến thức ngoài"
            }[criterion]
            msg += f"  {label}: {count} ({percentage:.1f}%)\n"
        
        messagebox.showinfo("Summary Statistics", msg)
    
    def export_json(self):
        if not self.segments:
            messagebox.showinfo("No Data", "No questions to export.")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if not file_path:
                return
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "source_file": os.path.basename(self.xml_file_path) if hasattr(self, 'xml_file_path') else "unknown",
                "checklist_summary": {},  # New section for checkbox counts and percentages
                "questions": []
            }
            
            total_questions = len(self.segments)
            checked_questions = sum(1 for qid in [s["question_id"] for s in self.segments] 
                                   if qid in self.checklist and any(self.checklist[qid].values()))
            
            # Calculate counts and percentages for each checkbox
            counts = {
                "single_sentence": 0,
                "multiple_sentences": 0,
                "low_quality_distractors": 0,
                "unsuitable_paragraph": 0,
                "unclear_answer": 0,
                "outside_knowledge": 0
            }
            for qid in [s["question_id"] for s in self.segments]:
                if qid in self.checklist:
                    for criterion, checked in self.checklist[qid].items():
                        if checked:
                            counts[criterion] += 1
            
            checklist_labels = {
                "single_sentence": "Cần một câu",
                "multiple_sentences": "Cần nhiều câu",
                "low_quality_distractors": "Lựa chọn sai kém chất lượng",
                "unsuitable_paragraph": "Đoạn văn không phù hợp",
                "unclear_answer": "Đáp án không rõ ràng",
                "outside_knowledge": "Cần kiến thức ngoài"
            }
            export_data["checklist_summary"] = {
                criterion: {
                    "label": checklist_labels[criterion],
                    "count": count,
                    "percentage": round(count / total_questions * 100, 2) if total_questions else 0
                }
                for criterion, count in counts.items()
            }

            # Existing metadata with checklist_percentages
            export_data["metadata"] = {
                "total_questions": total_questions,
                "questions_checked": checked_questions,
                "completion_percentage": round((checked_questions / total_questions) * 100, 1) if total_questions else 0,
                "checklist_percentages": {
                    criterion: round(count / total_questions * 100, 2) if total_questions else 0
                    for criterion, count in counts.items()
                }
            }
            
            # Populate questions data
            for segment in self.segments:
                question_id = segment["question_id"]
                segment_id = segment["segment_id"]
                
                question_data = {
                    "question_id": question_id,
                    "segment_id": segment_id,
                    "document_title": segment["document_title"],
                    "segment_title": segment.get("segment_title", ""),
                    "question_type": segment.get("question_type", ""),
                    "checklist": self.checklist.get(question_id, {
                        "single_sentence": False,
                        "multiple_sentences": False,
                        "low_quality_distractors": False,
                        "unsuitable_paragraph": False,
                        "unclear_answer": False,
                        "outside_knowledge": False
                    }),
                    "comment": self.comments.get(question_id, "")
                }
                
                export_data["questions"].append(question_data)
            
            # Write JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            # Update export message to show checklist summary
            msg = f"Results exported to:\n{file_path}\n\n"
            msg += f"Summary Statistics:\n"
            msg += f"Total questions: {total_questions}\n"
            msg += f"Questions checked: {checked_questions} ({checked_questions/total_questions*100:.1f}%)\n"
            msg += "Checklist summary:\n"
            for criterion, data in export_data["checklist_summary"].items():
                msg += f"  {data['label']}: {data['count']} ({data['percentage']:.1f}%)\n"
            
            messagebox.showinfo("Export Complete", msg)
            self.status_label.config(text=f"Exported results to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def on_closing(self):
        if hasattr(self, 'xml_file_path') and self.segments:
            self.save_progress(silent=True)
        self.root.destroy()

def main():
    import argparse
    parser = argparse.ArgumentParser(description='XML Question Validator')
    parser.add_argument('xml_file', nargs='?', help='XML file to validate')
    args = parser.parse_args()
    
    root = tk.Tk()
    app = CompactXMLValidator(root, args.xml_file)
    root.mainloop()

if __name__ == "__main__":
    main()