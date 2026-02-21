#!/usr/bin/env python3
"""
Hillshade to MBTiles Converter
Converts GeoTIFF DEM files to hillshade MBTiles for offline map viewing
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import sys
import tempfile
import shutil
from pathlib import Path
import threading
from PIL import Image, ImageTk


# Setup PATH for bundled GDAL (when running as PyInstaller executable)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = sys._MEIPASS
    bin_path = os.path.join(base_path, 'bin')
    if os.path.exists(bin_path):
        os.environ['PATH'] = bin_path + os.pathsep + os.environ.get('PATH', '')


class HillshadeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Hillshade to MBTiles Converter")
        self.root.geometry("800x850")
        
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.z_factor = tk.DoubleVar(value=1.0)
        self.azimuth = tk.DoubleVar(value=315.0)
        self.altitude = tk.DoubleVar(value=45.0)
        self.min_zoom = tk.IntVar(value=10)
        self.max_zoom = tk.IntVar(value=17)
        self.is_processing = False
        self.preview_window = None
        self.preview_hillshade_path = None
        
        self.create_ui()
        self.check_gdal()
    
    def create_ui(self):
        # Title
        title = ttk.Label(self.root, text="Hillshade to MBTiles Converter", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Input file selection
        input_frame = ttk.LabelFrame(self.root, text="Input GeoTIFF (DEM)", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Entry(input_frame, textvariable=self.input_path, width=60).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Browse...", command=self.browse_input).pack(side="left")
        
        # Output file selection
        output_frame = ttk.LabelFrame(self.root, text="Output MBTiles", padding=10)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_path, width=60).pack(side="left", padx=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).pack(side="left")
        
        # Parameters
        params_frame = ttk.LabelFrame(self.root, text="Parameters", padding=10)
        params_frame.pack(fill="x", padx=10, pady=5)
        
        # Z-factor
        ttk.Label(params_frame, text="Z-Factor (vertical exaggeration):").grid(row=0, column=0, sticky="w", pady=5)
        z_scale = ttk.Scale(params_frame, from_=0.1, to=10.0, variable=self.z_factor, 
                           orient="horizontal", length=200)
        z_scale.grid(row=0, column=1, padx=5)
        ttk.Label(params_frame, textvariable=self.z_factor).grid(row=0, column=2)
        
        # Azimuth
        ttk.Label(params_frame, text="Azimuth (light direction):").grid(row=1, column=0, sticky="w", pady=5)
        az_scale = ttk.Scale(params_frame, from_=0, to=360, variable=self.azimuth, 
                            orient="horizontal", length=200)
        az_scale.grid(row=1, column=1, padx=5)
        ttk.Label(params_frame, textvariable=self.azimuth).grid(row=1, column=2)
        
        # Altitude
        ttk.Label(params_frame, text="Altitude (light angle):").grid(row=2, column=0, sticky="w", pady=5)
        alt_scale = ttk.Scale(params_frame, from_=0, to=90, variable=self.altitude, 
                             orient="horizontal", length=200)
        alt_scale.grid(row=2, column=1, padx=5)
        ttk.Label(params_frame, textvariable=self.altitude).grid(row=2, column=2)
        
        # Zoom levels
        zoom_frame = ttk.Frame(params_frame)
        zoom_frame.grid(row=3, column=0, columnspan=3, pady=5, sticky="w")
        
        ttk.Label(zoom_frame, text="Min Zoom:").pack(side="left", padx=5)
        ttk.Spinbox(zoom_frame, from_=0, to=24, textvariable=self.min_zoom, width=5).pack(side="left")
        ttk.Label(zoom_frame, text="Max Zoom:").pack(side="left", padx=(20, 5))
        ttk.Spinbox(zoom_frame, from_=0, to=24, textvariable=self.max_zoom, width=5).pack(side="left")
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress.pack(fill="x", padx=10, pady=10)
        
        # Log output
        log_frame = ttk.LabelFrame(self.root, text="Processing Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True)
        
        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.preview_btn = ttk.Button(button_frame, text="Generate Preview", 
                                      command=self.start_preview)
        self.preview_btn.pack(side="left", padx=5)
        
        self.convert_btn = ttk.Button(button_frame, text="Convert to MBTiles", 
                                      command=self.start_conversion, style="Accent.TButton")
        self.convert_btn.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side="right", padx=5)
    
    def check_gdal(self):
        """Check if GDAL is available and add Homebrew paths if needed"""
        # Common GDAL installation paths
        possible_gdaldem_paths = [
            '/opt/homebrew/bin/gdaldem',  # Apple Silicon
            '/usr/local/bin/gdaldem',     # Intel Mac
            '/opt/homebrew/opt/gdal/bin/gdaldem',
            '/usr/local/opt/gdal/bin/gdaldem',
            'gdaldem'  # Try system PATH as fallback
        ]
        
        # Find the first working gdaldem
        for path in possible_gdaldem_paths:
            try:
                # For absolute paths, check if file exists first
                if path.startswith('/') and not os.path.exists(path):
                    continue
                    
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                # Check if output contains "GDAL" (check both stdout and stderr)
                output = result.stdout + result.stderr
                if result.returncode == 0 or "GDAL" in output or result.returncode == 1:
                    # Update PATH to include this directory
                    if path.startswith('/'):
                        gdal_dir = os.path.dirname(os.path.abspath(path))
                        if gdal_dir not in os.environ.get('PATH', ''):
                            os.environ['PATH'] = gdal_dir + os.pathsep + os.environ.get('PATH', '')
                    
                    version_text = output.strip() if output.strip() else "GDAL"
                    self.log(f"✓ GDAL found: {version_text}")
                    self.log(f"  Using: {path}")
                    return
                    
            except FileNotFoundError:
                # Command not found, try next path
                continue
            except Exception as e:
                continue
        
        # GDAL not found
        self.log("⚠ GDAL not found in common locations")
        messagebox.showwarning("GDAL Not Found", 
            "GDAL is required but not found.\n\n"
            "Please install GDAL:\n"
            "  macOS: brew install gdal\n"
            "  Windows: Download from gisinternals.com\n"
            "  Linux: sudo apt install gdal-bin\n\n"
            "After installing, restart the application.")
    
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select Input GeoTIFF",
            filetypes=[("GeoTIFF files", "*.tif *.tiff"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            # Auto-generate output path
            output = Path(filename).with_suffix('.mbtiles')
            output = output.with_name(output.stem + '_hillshade.mbtiles')
            self.output_path.set(str(output))
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save MBTiles As",
            defaultextension=".mbtiles",
            filetypes=[("MBTiles files", "*.mbtiles"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def start_preview(self):
        """Start preview generation in background thread"""
        if self.is_processing:
            return
        
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input file")
            return
        
        self.is_processing = True
        self.preview_btn.config(state="disabled")
        self.convert_btn.config(state="disabled")
        self.progress_var.set(0)
        
        thread = threading.Thread(target=self.generate_preview)
        thread.daemon = True
        thread.start()
    
    def generate_preview(self):
        """Generate hillshade preview"""
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix='hillshade_preview_')
            self.log("\nGenerating hillshade preview...")
            
            hillshade_path = os.path.join(temp_dir, 'hillshade_preview.tif')
            self.preview_hillshade_path = hillshade_path
            
            self.progress_var.set(50)
            self.run_command([
                'gdaldem', 'hillshade',
                self.input_path.get(),
                hillshade_path,
                '-z', str(self.z_factor.get()),
                '-az', str(self.azimuth.get()),
                '-alt', str(self.altitude.get()),
                '-compute_edges'
            ])
            
            self.progress_var.set(100)
            self.log("✓ Preview generated successfully!")
            
            # Show preview window
            self.show_preview_window(hillshade_path)
            
        except Exception as e:
            self.log(f"\n✗ ERROR: {str(e)}")
            messagebox.showerror("Error", f"Preview generation failed:\n{str(e)}")
        finally:
            self.is_processing = False
            self.preview_btn.config(state="normal")
            self.convert_btn.config(state="normal")
    
    def show_preview_window(self, hillshade_path):
        """Display the hillshade preview in a new window"""
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
        
        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("Hillshade Preview")
        self.preview_window.geometry("800x650")
        
        # Read and display the hillshade using PIL
        try:
            # Use gdal_translate to convert to PNG first for easier reading
            temp_png = hillshade_path.replace('.tif', '_preview.png')
            subprocess.run([
                'gdal_translate',
                '-of', 'PNG',
                '-scale',
                hillshade_path,
                temp_png
            ], check=True, capture_output=True)
            
            # Open with PIL
            img = Image.open(temp_png)
            width, height = img.size
            
            # Resize for display if too large
            max_display_size = 750
            if width > max_display_size or height > max_display_size:
                scale = min(max_display_size / width, max_display_size / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Display in label
            preview_label = ttk.Label(self.preview_window, image=photo)
            preview_label.image = photo  # Keep reference
            preview_label.pack(padx=10, pady=10)
            
            # Clean up temp PNG
            try:
                os.remove(temp_png)
            except:
                pass
            
            # Info label
            info_text = (f"Size: {width} x {height} pixels\n"
                        f"Z-Factor: {self.z_factor.get()}, "
                        f"Azimuth: {self.azimuth.get()}°, "
                        f"Altitude: {self.altitude.get()}°")
            info_label = ttk.Label(self.preview_window, text=info_text, 
                                  font=("Arial", 10), justify="center")
            info_label.pack(pady=5)
            
            # Buttons
            btn_frame = ttk.Frame(self.preview_window)
            btn_frame.pack(pady=10)
            
            ttk.Button(btn_frame, text="Regenerate with New Parameters", 
                      command=lambda: [self.preview_window.destroy(), self.start_preview()]).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Close", 
                      command=self.preview_window.destroy).pack(side="left", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display preview:\n{str(e)}")
            if self.preview_window and self.preview_window.winfo_exists():
                self.preview_window.destroy()
    
    def start_conversion(self):
        """Start conversion in background thread"""
        if self.is_processing:
            return
        
        if not self.input_path.get() or not self.output_path.get():
            messagebox.showerror("Error", "Please select input and output files")
            return
        
        self.is_processing = True
        self.convert_btn.config(state="disabled")
        self.progress_var.set(0)
        
        thread = threading.Thread(target=self.convert)
        thread.daemon = True
        thread.start()
    
    def convert(self):
        """Perform the conversion"""
        try:
            # Ensure output directory exists and is writable
            output_path = self.output_path.get()
            output_dir = os.path.dirname(output_path)
            
            if output_dir and not os.path.exists(output_dir):
                self.log(f"Creating output directory: {output_dir}")
                os.makedirs(output_dir, exist_ok=True)
            
            # Check if we can write to the output location
            if output_dir:
                test_file = os.path.join(output_dir, '.write_test')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                except (PermissionError, OSError) as e:
                    raise PermissionError(
                        f"Cannot write to directory: {output_dir}\n"
                        f"Error: {e}\n\n"
                        f"This directory may have restricted permissions.\n"
                        f"Try saving to a different location like:\n"
                        f"  • Desktop\n"
                        f"  • Documents\n"
                        f"  • A folder you created"
                    )
            
            # Remove existing output file if present
            if os.path.exists(output_path):
                self.log(f"Removing existing file: {output_path}")
                try:
                    os.remove(output_path)
                except OSError as e:
                    raise PermissionError(f"Cannot remove existing file: {output_path}\nError: {e}")

            
            temp_dir = tempfile.mkdtemp(prefix='hillshade_')
            self.log(f"Created temporary directory: {temp_dir}")
            
            # Step 1: Generate hillshade
            self.progress_var.set(10)
            self.log("\nStep 1/4: Analyzing input and generating hillshade...")
            
            # Check input resolution to understand appropriate zoom levels
            self.log("\nInput file information:")
            self.run_command(['gdalinfo', self.input_path.get()])
            self.log("")
            
            hillshade_path = os.path.join(temp_dir, 'hillshade_raw.tif')
            self.run_command([
                'gdaldem', 'hillshade',
                self.input_path.get(),
                hillshade_path,
                '-z', str(self.z_factor.get()),
                '-az', str(self.azimuth.get()),
                '-alt', str(self.altitude.get()),
                '-compute_edges'
            ])
            
            # Convert to explicit greyscale to ensure no color tinting
            self.log("\nConverting to greyscale...")
            greyscale_path = os.path.join(temp_dir, 'hillshade_grey.tif')
            self.run_command([
                'gdal_translate',
                '-ot', 'Byte',
                '-co', 'PHOTOMETRIC=MINISBLACK',
                hillshade_path,
                greyscale_path
            ])
            hillshade_path = greyscale_path
            
            # Step 2: Warp to Web Mercator
            self.progress_var.set(30)
            self.log("\nStep 2/4: Reprojecting to Web Mercator EPSG:3857...")
            warped_path = os.path.join(temp_dir, 'hillshade_mercator.tif')
            self.run_command([
                'gdalwarp',
                '-t_srs', 'EPSG:3857',
                '-r', 'bilinear',
                '-co', 'TILED=YES',
                '-co', 'COMPRESS=DEFLATE',
                hillshade_path,
                warped_path
            ])
            
           # Step 3: Convert to MBTiles with proper zoom levels
            self.progress_var.set(60)
            self.log("\nStep 3/4: Converting to MBTiles format...")
            self.log(f"Zoom levels: {self.min_zoom.get()} to {self.max_zoom.get()}")
            self.log("")
            self.log("IMPORTANT: Using UPPER zoom strategy to create tiles at all zoom levels.")
            self.log("Tiles may appear stretched at higher zoom if input resolution is insufficient.")
            self.log("")
            
            # Calculate the zoom level span for overview generation
            zoom_span = self.max_zoom.get() - self.min_zoom.get()
            
            self.run_command([
                'gdal_translate',
                '-of', 'MBTiles',
                '-co', 'TILE_FORMAT=PNG',
                '-co', 'RESAMPLING=AVERAGE',
                '-co', f'MINZOOM={self.min_zoom.get()}',
                '-co', f'MAXZOOM={self.max_zoom.get()}',
                '-co', 'ZOOM_LEVEL_STRATEGY=UPPER',
                warped_path,
                self.output_path.get()
            ])
            
            # Step 4: Verify output
            self.progress_var.set(90)
            self.log("\nStep 4/4: Verifying MBTiles output...")
            self.log("Checking zoom levels in generated MBTiles...")
            
            # Query the MBTiles to show what zoom levels were created
            try:
                import sqlite3
                conn = sqlite3.connect(self.output_path.get())
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT zoom_level FROM tiles ORDER BY zoom_level")
                zoom_levels = [row[0] for row in cursor.fetchall()]
                conn.close()
                self.log(f"Created tiles at zoom levels: {zoom_levels}")
                
                if len(zoom_levels) < zoom_span + 1:
                    self.log("WARNING: Not all zoom levels have tiles. This may cause visibility issues.")
                    self.log("Try using a higher resolution input file or reducing MAXZOOM.")
            except Exception as e:
                self.log(f"Could not verify zoom levels: {e}")
            
            # Cleanup
            self.log("\nCleaning up temporary files...")
            shutil.rmtree(temp_dir)
            
            self.progress_var.set(100)
            self.log("\n✓ Conversion complete!")
            self.log(f"Output saved to: {self.output_path.get()}")
            
            messagebox.showinfo("Success", 
                f"Hillshade conversion completed successfully!\n\n"
                f"Output: {self.output_path.get()}")
            
        except Exception as e:
            self.log(f"\n✗ ERROR: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed:\n{str(e)}")
        finally:
            self.is_processing = False
            self.convert_btn.config(state="normal")
    
    def run_command(self, cmd):
        """Run a command and log output"""
        self.log(f"Running: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            line = line.strip()
            if line:
                self.log(line)
        
        process.wait()
        
        if process.returncode != 0:
            raise RuntimeError(f"Command failed with exit code {process.returncode}")

def main():
    root = tk.Tk()
    
    # Style
    style = ttk.Style()
    style.theme_use('aqua' if sys.platform == 'darwin' else 'clam')
    
    app = HillshadeConverter(root)
    root.mainloop()

if __name__ == '__main__':
    main()
