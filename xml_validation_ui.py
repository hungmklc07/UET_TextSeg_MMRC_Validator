#!/usr/bin/env python3
"""
Compact XML Question Validation Tool

A lightweight validation tool for XML question data with all UI elements on a single screen.
Automatically saves progress when moving between questions or exiting.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import xml.etree.ElementTree as ET
import csv
import json
from datetime import datetime

class CompactXMLValidator:
    def __init__(self, root, xml_file=None):
        self.root = root
        self.root.title("XML Question Validator")
        self.root.geometry("1000x700")
        
        # Application state
        self.segments = []
        self.current_index = 0
        self.ratings = {}
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
        
        # Content area - all on one screen
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
        
        # Rating frame
        rating_frame = ttk.LabelFrame(right_frame, text="Rating (1-5 stars)")
        rating_frame.pack(fill=tk.X, pady=5)
        
        # Rating variable
        self.rating_var = tk.IntVar()
        
        # Rating buttons
        rating_buttons = ttk.Frame(rating_frame)
        rating_buttons.pack(pady=10)
        
        for i in range(1, 6):
            rb = ttk.Radiobutton(
                rating_buttons, 
                text=f"{i}", 
                variable=self.rating_var, 
                value=i,
                command=self.save_current_rating
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Comments frame
        comments_frame = ttk.LabelFrame(right_frame, text="Comments")
        comments_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.comments_text = scrolledtext.ScrolledText(comments_frame, wrap=tk.WORD)
        self.comments_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind event to save comment when text changes
        self.comments_text.bind("<KeyRelease>", self.save_current_comment)
        
        # Status bar at bottom
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
            
            # Store file path for later
            self.xml_file_path = file_path
            
            # Reset data
            self.segments = []
            
            # Debug print
            print(f"Root tag: {root.tag}")
            print(f"Number of children: {len(root)}")
            for i, child in enumerate(root):
                print(f"Child {i}: {child.tag} (id: {child.get('id', 'None')})")
            
            # Extract segments from XML
            for segment in root.findall("Segment"):
                segment_id = segment.get("id")
                
                # Get segment data
                segment_text = segment.find("SegmentText")
                if segment_text is None or not segment_text.text:
                    continue
                
                # Extract document and segment titles
                doc_title = segment.find("DocumentTitle")
                doc_title_text = doc_title.text if doc_title is not None else "Unknown"
                
                segment_title = segment.find("SegmentTitle")
                segment_title_text = segment_title.text if segment_title is not None else ""
                
                # Find QA element
                qa_elem = segment.find("QA")
                if qa_elem is None:
                    continue
                
                # Find questions within QA
                for question_elem in qa_elem.findall("Question"):
                    question_id = question_elem.get("id")
                    
                    # Get question type
                    question_type_elem = question_elem.find("QuestionType")
                    question_type = question_type_elem.text if question_type_elem is not None else ""
                    
                    # Get question text
                    question_text_elem = question_elem.find("QuestionText")
                    if question_text_elem is None or not question_text_elem.text:
                        continue
                    
                    # Get choices
                    choices_elem = question_elem.find("Choices")
                    if choices_elem is None:
                        continue
                    
                    choices = []
                    for choice_elem in choices_elem.findall("Choice"):
                        choice_id = choice_elem.get("id")
                        if choice_elem.text:
                            choices.append({"id": choice_id, "text": choice_elem.text})
                    
                    # Get correct choice
                    correct_choice_elem = question_elem.find("CorrectChoice")
                    correct_choice = correct_choice_elem.text if correct_choice_elem is not None else ""
                    
                    # Add to segments list
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
            
            # If no segments found with direct approach, try a more generic approach
            if not self.segments:
                print("No segments found with direct approach, trying more generic XPath...")
                # Try with any path
                for segment in root.findall(".//Segment"):
                    # Same processing as above...
                    segment_id = segment.get("id")
                    print(f"Found segment with XPath: {segment_id}")
                    
                    # Same extraction code as above...
                    # (omitted for brevity)
            
            # Load the first question if available
            if self.segments:
                print(f"Successfully loaded {len(self.segments)} questions")
                self.status_label.config(text=f"Loaded {len(self.segments)} questions from {os.path.basename(file_path)}")
                
                # Try to load saved progress
                self.try_load_progress()
                
                # Update progress
                self.update_progress_bar()
                
                # Set window title to include file name
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
        
        # Save current progress before changing
        self.auto_save_progress()
        
        # Get segment data
        data = self.segments[index]
        self.current_index = index
        
        # Update segment text
        self.segment_text.config(state=tk.NORMAL)
        self.segment_text.delete(1.0, tk.END)
        self.segment_text.insert(tk.END, data["segment_text"])
        self.segment_text.config(state=tk.DISABLED)
        
        # Update question text
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        question_header = f"({data['question_type']}) "
        self.question_text.insert(tk.END, question_header, "bold")
        self.question_text.insert(tk.END, data["question_text"])
        self.question_text.tag_configure("bold", font=("TkDefaultFont", 12, "bold"))
        self.question_text.config(state=tk.DISABLED)
        
        # Update choices
        for widget in self.choices_container.winfo_children():
            widget.destroy()
        
        for i, choice in enumerate(data["choices"]):
            is_correct = choice["id"] == data["correct_choice"]
            
            choice_frame = ttk.Frame(self.choices_container)
            choice_frame.pack(fill=tk.X, pady=2)
            
            # Use regular background but add a red checkmark for correct answer
            if is_correct:
                choice_label = tk.Label(
                    choice_frame, 
                    text=choice['text'], 
                    anchor="w",
                    wraplength=350,
                    justify=tk.LEFT
                )
                choice_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # Add red checkmark
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
        
        # Update navigation
        self.position_label.config(text=f"Question {index + 1} of {len(self.segments)}")
        self.prev_btn.config(state=tk.NORMAL if index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if index < len(self.segments) - 1 else tk.DISABLED)
        
        # Update rating and comment
        question_id = data["question_id"]
        self.rating_var.set(self.ratings.get(question_id, 0))
        
        self.comments_text.delete(1.0, tk.END)
        if question_id in self.comments:
            self.comments_text.insert(tk.END, self.comments[question_id])
        
        # Update progress bar
        self.update_progress_bar()
    
    def prev_question(self):
        if self.current_index > 0:
            self.load_question(self.current_index - 1)
    
    def next_question(self):
        if self.current_index < len(self.segments) - 1:
            self.load_question(self.current_index + 1)
    
    def save_current_rating(self):
        if not self.segments:
            return
            
        question_id = self.segments[self.current_index]["question_id"]
        rating = self.rating_var.get()
        
        if rating > 0:
            self.ratings[question_id] = rating
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
        
        # Count rated questions
        rated_count = sum(1 for r in self.ratings.values() if r > 0)
        progress_value = (rated_count / len(self.segments)) * 100
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
        
        # Calculate average rating for metadata
        total_rated = sum(1 for r in self.ratings.values() if r > 0)
        avg_rating = 0
        if total_rated > 0:
            avg_rating = sum(r for r in self.ratings.values() if r > 0) / total_rated
        
        progress_data = {
            "timestamp": datetime.now().isoformat(),
            "ratings": self.ratings,
            "comments": self.comments,
            "current_index": self.current_index,
            "metadata": {
                "total_questions": len(self.segments),
                "questions_rated": total_rated,
                "average_rating": round(avg_rating, 2),
                "completion_percentage": round((total_rated / len(self.segments)) * 100, 1) if self.segments else 0
            }
        }
        
        try:
            # Create filename based on the XML filename
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
        
        # Create filename based on the XML filename
        base_name = os.path.splitext(self.xml_file_path)[0]
        progress_file = f"{base_name}_progress.json"
        
        if not os.path.exists(progress_file):
            # No saved progress, just load the first question
            self.load_question(0)
            return
        
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "ratings" in data:
                self.ratings = data["ratings"]
            
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
            
            # Display metadata if available
            if "metadata" in data and data["metadata"].get("average_rating") is not None:
                avg = data["metadata"]["average_rating"]
                completed = data["metadata"].get("completion_percentage", 0)
                self.status_label.config(text=f"Loaded previous progress. Average rating: {avg}/5, Completion: {completed}%")
            else:
                self.status_label.config(text=f"Loaded previous progress from {os.path.basename(progress_file)}")
        except Exception as e:
            print(f"Failed to load progress: {str(e)}")
            self.load_question(0)
    
    def show_summary(self):
        """Show a summary of the current validation progress"""
        if not self.segments:
            messagebox.showinfo("No Data", "No questions loaded yet.")
            return
        
        # Calculate statistics
        total_questions = len(self.segments)
        rated_questions = sum(1 for qid in [s["question_id"] for s in self.segments] if qid in self.ratings and self.ratings[qid] > 0)
        commented_questions = sum(1 for qid in [s["question_id"] for s in self.segments] if qid in self.comments and self.comments[qid])
        
        avg_rating = 0
        if rated_questions > 0:
            avg_rating = sum(r for r in self.ratings.values() if r > 0) / rated_questions
        
        # Count by rating
        rating_counts = {i: 0 for i in range(1, 6)}
        for r in self.ratings.values():
            if r > 0:
                rating_counts[r] += 1
        
        # Create summary message
        msg = "VALIDATION SUMMARY\n\n"
        msg += f"Total questions: {total_questions}\n"
        msg += f"Questions rated: {rated_questions} ({rated_questions/total_questions*100:.1f}%)\n"
        msg += f"Questions with comments: {commented_questions}\n"
        msg += f"Average rating: {avg_rating:.1f}/5\n\n"
        
        msg += "Rating distribution:\n"
        for i in range(1, 6):
            count = rating_counts[i]
            percentage = count/total_questions*100 if total_questions > 0 else 0
            msg += f"  {i} star{'s' if i > 1 else ''}: {count} ({percentage:.1f}%)\n"
        
        messagebox.showinfo("Summary Statistics", msg)
    
    def export_json(self):
        """Export validation results to JSON with metadata"""
        if not self.segments:
            messagebox.showinfo("No Data", "No questions to export.")
            return
        
        try:
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Prepare export data
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "source_file": os.path.basename(self.xml_file_path) if hasattr(self, 'xml_file_path') else "unknown",
                "questions": []
            }
            
            # Calculate metadata
            total_questions = len(self.segments)
            rated_questions = sum(1 for qid in [s["question_id"] for s in self.segments] if qid in self.ratings and self.ratings[qid] > 0)
            
            avg_rating = 0
            if rated_questions > 0:
                avg_rating = sum(r for r in self.ratings.values() if r > 0) / rated_questions
            
            # Add metadata
            export_data["metadata"] = {
                "total_questions": total_questions,
                "questions_rated": rated_questions,
                "average_rating": round(avg_rating, 2),
                "completion_percentage": round((rated_questions / total_questions) * 100, 1) if total_questions > 0 else 0
            }
            
            # Add each question's data
            for segment in self.segments:
                question_id = segment["question_id"]
                segment_id = segment["segment_id"]
                
                question_data = {
                    "question_id": question_id,
                    "segment_id": segment_id,
                    "document_title": segment["document_title"],
                    "segment_title": segment.get("segment_title", ""),
                    "question_type": segment.get("question_type", ""),
                    "rating": self.ratings.get(question_id, None),
                    "comment": self.comments.get(question_id, "")
                }
                
                export_data["questions"].append(question_data)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            # Show success message with statistics
            msg = f"Results exported to:\n{file_path}\n\n"
            msg += f"Summary Statistics:\n"
            msg += f"Total questions: {total_questions}\n"
            msg += f"Questions rated: {rated_questions} ({rated_questions/total_questions*100:.1f}%)\n"
            msg += f"Average rating: {avg_rating:.1f}/5"
            
            messagebox.showinfo("Export Complete", msg)
            
            self.status_label.config(text=f"Exported results to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def on_closing(self):
        # Save progress before exiting
        if hasattr(self, 'xml_file_path') and self.segments:
            self.save_progress(silent=True)
        self.root.destroy()

# Main function
def main():
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='XML Question Validator')
    parser.add_argument('xml_file', nargs='?', help='XML file to validate')
    args = parser.parse_args()
    
    # Create the main window
    root = tk.Tk()
    app = CompactXMLValidator(root, args.xml_file)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()