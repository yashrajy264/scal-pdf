#!/usr/bin/env python3
"""
ScalPDF Package Testing Suite
Comprehensive testing for all ScalPDF packages and installations.
"""

import os
import sys
import subprocess
import platform
import shutil
import tempfile
import time
import json
from pathlib import Path
from datetime import datetime

class PackageTester:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_info(),
            'tests': {}
        }
        
    def get_system_info(self):
        """Get system information."""
        return {
            'os': platform.system(),
            'dist': self.get_linux_dist(),
            'arch': platform.machine(),
            'python': platform.python_version(),
            'kernel': platform.release() if platform.system() == 'Linux' else None
        }
        
    def get_linux_dist(self):
        """Get Linux distribution info."""
        if platform.system() != 'Linux':
            return None
            
        try:
            with open('/etc/os-release', 'r') as f:
                info = {}
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        info[key] = value.strip('"')
                return f"{info.get('NAME', 'Unknown')} {info.get('VERSION', '')}"
        except:
            return "Unknown Linux"
            
    def log(self, message, level="INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️ ",
            "TEST": "🧪"
        }.get(level, "  ")
        
        print(f"[{timestamp}] {prefix} {message}")
        
    def run_command(self, command, timeout=30, capture=True):
        """Run a command and return result."""
        try:
            if capture:
                result = subprocess.run(
                    command, 
                    capture_output=True, 
                    text=True, 
                    timeout=timeout,
                    shell=isinstance(command, str)
                )
                return {
                    'success': result.returncode == 0,
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                result = subprocess.run(
                    command,
                    timeout=timeout,
                    shell=isinstance(command, str)
                )
                return {
                    'success': result.returncode == 0,
                    'returncode': result.returncode,
                    'stdout': '',
                    'stderr': ''
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }
            
    def test_build_environment(self):
        """Test the build environment."""
        self.log("Testing build environment...", "TEST")
        
        tests = {
            'python_version': self.test_python_version(),
            'required_tools': self.test_required_tools(),
            'project_structure': self.test_project_structure(),
            'dependencies': self.test_dependencies()
        }
        
        self.test_results['tests']['build_environment'] = tests
        
        success_count = sum(1 for test in tests.values() if test['success'])
        total_count = len(tests)
        
        if success_count == total_count:
            self.log(f"Build environment: {success_count}/{total_count} tests passed", "SUCCESS")
        else:
            self.log(f"Build environment: {success_count}/{total_count} tests passed", "WARNING")
            
        return success_count == total_count
        
    def test_python_version(self):
        """Test Python version."""
        try:
            version = sys.version_info
            required = (3, 11)
            
            if version >= required:
                return {
                    'success': True,
                    'message': f"Python {version.major}.{version.minor}.{version.micro}",
                    'details': 'Version requirement met'
                }
            else:
                return {
                    'success': False,
                    'message': f"Python {version.major}.{version.minor}.{version.micro}",
                    'details': f'Requires Python {required[0]}.{required[1]}+'
                }
        except Exception as e:
            return {
                'success': False,
                'message': 'Failed to check Python version',
                'details': str(e)
            }
            
    def test_required_tools(self):
        """Test required build tools."""
        tools = {
            'python3': 'python3 --version',
            'pip': 'pip --version',
            'git': 'git --version'
        }
        
        optional_tools = {
            'dpkg-deb': 'dpkg-deb --version',
            'snapcraft': 'snapcraft --version',
            'docker': 'docker --version'
        }
        
        results = {}
        
        # Test required tools
        for tool, command in tools.items():
            result = self.run_command(command.split())
            results[tool] = {
                'required': True,
                'available': result['success'],
                'version': result['stdout'].strip() if result['success'] else None
            }
        
        # Test optional tools
        for tool, command in optional_tools.items():
            result = self.run_command(command.split())
            results[tool] = {
                'required': False,
                'available': result['success'],
                'version': result['stdout'].strip() if result['success'] else None
            }
        
        # Check if all required tools are available
        required_available = all(
            results[tool]['available'] 
            for tool in tools.keys()
        )
        
        return {
            'success': required_available,
            'message': 'Required tools check',
            'details': results
        }
        
    def test_project_structure(self):
        """Test project structure."""
        required_files = [
            'main.py',
            'requirements.txt',
            'core/__init__.py',
            'ui/__init__.py',
            'cli/__init__.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        return {
            'success': len(missing_files) == 0,
            'message': 'Project structure check',
            'details': {
                'required_files': required_files,
                'missing_files': missing_files
            }
        }
        
    def test_dependencies(self):
        """Test Python dependencies."""
        requirements_file = self.project_root / 'requirements.txt'
        
        if not requirements_file.exists():
            return {
                'success': False,
                'message': 'requirements.txt not found',
                'details': None
            }
        
        # Try to install dependencies in a temporary venv
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_dir = Path(temp_dir) / 'test_venv'
            
            # Create venv
            result = self.run_command([sys.executable, '-m', 'venv', str(venv_dir)])
            if not result['success']:
                return {
                    'success': False,
                    'message': 'Failed to create test virtual environment',
                    'details': result['stderr']
                }
            
            # Install dependencies
            pip_path = venv_dir / 'bin' / 'pip' if platform.system() != 'Windows' else venv_dir / 'Scripts' / 'pip.exe'
            
            result = self.run_command([
                str(pip_path), 'install', '-r', str(requirements_file)
            ], timeout=120)
            
            return {
                'success': result['success'],
                'message': 'Dependencies installation test',
                'details': {
                    'stdout': result['stdout'][-500:] if result['stdout'] else '',  # Last 500 chars
                    'stderr': result['stderr'][-500:] if result['stderr'] else ''
                }
            }
            
    def test_package_builders(self):
        """Test package builders."""
        self.log("Testing package builders...", "TEST")
        
        builders = {
            'appimage': 'build_appimage.py',
            'deb': 'build_deb.py',
            'snap': 'build_snap.py'
        }
        
        tests = {}
        
        for package_type, builder_script in builders.items():
            self.log(f"Testing {package_type} builder...", "INFO")
            
            builder_path = self.project_root / "Installers GUI" / builder_script
            
            if not builder_path.exists():
                tests[package_type] = {
                    'success': False,
                    'message': f'{builder_script} not found',
                    'details': None
                }
                continue
            
            # Test builder script syntax
            result = self.run_command([
                sys.executable, '-m', 'py_compile', str(builder_path)
            ])
            
            if result['success']:
                # Test help option
                help_result = self.run_command([
                    sys.executable, str(builder_path), '--help'
                ])
                
                tests[package_type] = {
                    'success': help_result['success'],
                    'message': f'{package_type} builder syntax and help',
                    'details': {
                        'syntax_check': True,
                        'help_available': help_result['success'],
                        'help_output': help_result['stdout'][:200] if help_result['stdout'] else ''
                    }
                }
            else:
                tests[package_type] = {
                    'success': False,
                    'message': f'{package_type} builder syntax error',
                    'details': result['stderr']
                }
        
        self.test_results['tests']['package_builders'] = tests
        
        success_count = sum(1 for test in tests.values() if test['success'])
        total_count = len(tests)
        
        if success_count == total_count:
            self.log(f"Package builders: {success_count}/{total_count} tests passed", "SUCCESS")
        else:
            self.log(f"Package builders: {success_count}/{total_count} tests passed", "WARNING")
            
        return success_count == total_count
        
    def test_gui_installer(self):
        """Test GUI installer."""
        self.log("Testing GUI installer...", "TEST")
        
        installer_path = self.project_root / "Installers GUI" / "package_installer.py"
        
        if not installer_path.exists():
            test_result = {
                'success': False,
                'message': 'package_installer.py not found',
                'details': None
            }
        else:
            # Test syntax
            syntax_result = self.run_command([
                sys.executable, '-m', 'py_compile', str(installer_path)
            ])
            
            if syntax_result['success']:
                # Test help
                help_result = self.run_command([
                    sys.executable, str(installer_path), '--help'
                ])
                
                test_result = {
                    'success': help_result['success'],
                    'message': 'GUI installer syntax and help',
                    'details': {
                        'syntax_check': True,
                        'help_available': help_result['success']
                    }
                }
            else:
                test_result = {
                    'success': False,
                    'message': 'GUI installer syntax error',
                    'details': syntax_result['stderr']
                }
        
        self.test_results['tests']['gui_installer'] = test_result
        
        if test_result['success']:
            self.log("GUI installer: Test passed", "SUCCESS")
        else:
            self.log("GUI installer: Test failed", "ERROR")
            
        return test_result['success']
        
    def test_smart_launcher(self):
        """Test smart launcher."""
        self.log("Testing smart launcher...", "TEST")
        
        launcher_path = self.project_root / "Installers GUI" / "smart_launcher.py"
        
        if not launcher_path.exists():
            test_result = {
                'success': False,
                'message': 'smart_launcher.py not found',
                'details': None
            }
        else:
            # Test syntax
            syntax_result = self.run_command([
                sys.executable, '-m', 'py_compile', str(launcher_path)
            ])
            
            if syntax_result['success']:
                # Test help and info options
                help_result = self.run_command([
                    sys.executable, str(launcher_path), '--help'
                ])
                
                info_result = self.run_command([
                    sys.executable, str(launcher_path), '--info'
                ])
                
                test_result = {
                    'success': help_result['success'] and info_result['success'],
                    'message': 'Smart launcher functionality',
                    'details': {
                        'syntax_check': True,
                        'help_available': help_result['success'],
                        'info_available': info_result['success']
                    }
                }
            else:
                test_result = {
                    'success': False,
                    'message': 'Smart launcher syntax error',
                    'details': syntax_result['stderr']
                }
        
        self.test_results['tests']['smart_launcher'] = test_result
        
        if test_result['success']:
            self.log("Smart launcher: Test passed", "SUCCESS")
        else:
            self.log("Smart launcher: Test failed", "ERROR")
            
        return test_result['success']
        
    def test_existing_packages(self):
        """Test existing packages."""
        self.log("Testing existing packages...", "TEST")
        
        build_dir = self.project_root / "build"
        tests = {}
        
        if not build_dir.exists():
            tests['no_build_dir'] = {
                'success': True,
                'message': 'No build directory found (expected for fresh setup)',
                'details': None
            }
        else:
            # Test AppImages
            appimages = list(build_dir.glob("**/*.AppImage"))
            if appimages:
                for appimage in appimages:
                    test_name = f"appimage_{appimage.name}"
                    
                    # Check if executable
                    executable = os.access(appimage, os.X_OK)
                    
                    # Check size
                    size_mb = appimage.stat().st_size / (1024 * 1024)
                    
                    tests[test_name] = {
                        'success': executable and size_mb > 0.1,  # At least 100KB
                        'message': f'AppImage: {appimage.name}',
                        'details': {
                            'path': str(appimage),
                            'executable': executable,
                            'size_mb': round(size_mb, 1)
                        }
                    }
            
            # Test .deb packages
            debs = list(build_dir.glob("**/*.deb"))
            if debs:
                for deb in debs:
                    test_name = f"deb_{deb.name}"
                    
                    # Check size
                    size_mb = deb.stat().st_size / (1024 * 1024)
                    
                    # Try to get package info
                    info_result = self.run_command([
                        'dpkg-deb', '--info', str(deb)
                    ]) if shutil.which('dpkg-deb') else {'success': False}
                    
                    tests[test_name] = {
                        'success': size_mb > 0.1 and info_result['success'],
                        'message': f'DEB package: {deb.name}',
                        'details': {
                            'path': str(deb),
                            'size_mb': round(size_mb, 1),
                            'valid_package': info_result['success']
                        }
                    }
            
            # Test Snap packages
            snaps = list(build_dir.glob("**/*.snap"))
            if snaps:
                for snap in snaps:
                    test_name = f"snap_{snap.name}"
                    
                    # Check size
                    size_mb = snap.stat().st_size / (1024 * 1024)
                    
                    tests[test_name] = {
                        'success': size_mb > 0.1,
                        'message': f'Snap package: {snap.name}',
                        'details': {
                            'path': str(snap),
                            'size_mb': round(size_mb, 1)
                        }
                    }
        
        self.test_results['tests']['existing_packages'] = tests
        
        if tests:
            success_count = sum(1 for test in tests.values() if test['success'])
            total_count = len(tests)
            
            if success_count == total_count:
                self.log(f"Existing packages: {success_count}/{total_count} tests passed", "SUCCESS")
            else:
                self.log(f"Existing packages: {success_count}/{total_count} tests passed", "WARNING")
                
            return success_count == total_count
        else:
            self.log("No existing packages found", "INFO")
            return True
            
    def generate_report(self):
        """Generate test report."""
        self.log("Generating test report...", "INFO")
        
        # Calculate overall statistics
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.test_results['tests'].items():
            if isinstance(tests, dict):
                if 'success' in tests:
                    # Single test
                    total_tests += 1
                    if tests['success']:
                        passed_tests += 1
                else:
                    # Multiple tests
                    for test_name, test_result in tests.items():
                        if isinstance(test_result, dict) and 'success' in test_result:
                            total_tests += 1
                            if test_result['success']:
                                passed_tests += 1
        
        # Create report
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'overall_success': passed_tests == total_tests
            },
            'system_info': self.test_results['system'],
            'timestamp': self.test_results['timestamp'],
            'detailed_results': self.test_results['tests']
        }
        
        # Save report
        report_file = self.project_root / "build" / "test_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST REPORT SUMMARY")
        print("=" * 60)
        print(f"System: {report['system_info']['os']} {report['system_info']['dist'] or ''}")
        print(f"Architecture: {report['system_info']['arch']}")
        print(f"Python: {report['system_info']['python']}")
        print(f"Timestamp: {report['timestamp']}")
        print()
        print(f"Tests Run: {total_tests}")
        print(f"Tests Passed: {passed_tests}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print()
        
        if report['summary']['overall_success']:
            print("✅ ALL TESTS PASSED - ScalPDF is ready for use!")
        else:
            print("⚠️  SOME TESTS FAILED - Check detailed results")
            
        print(f"\n📄 Detailed report saved to: {report_file}")
        print("=" * 60)
        
        return report
        
    def run_all_tests(self):
        """Run all tests."""
        self.log("Starting ScalPDF package testing suite...", "INFO")
        print(f"System: {self.test_results['system']['os']} {self.test_results['system']['dist'] or ''}")
        print(f"Architecture: {self.test_results['system']['arch']}")
        print()
        
        # Run test categories
        test_categories = [
            ('Build Environment', self.test_build_environment),
            ('Package Builders', self.test_package_builders),
            ('GUI Installer', self.test_gui_installer),
            ('Smart Launcher', self.test_smart_launcher),
            ('Existing Packages', self.test_existing_packages)
        ]
        
        results = []
        
        for category_name, test_func in test_categories:
            try:
                result = test_func()
                results.append(result)
            except Exception as e:
                self.log(f"Test category '{category_name}' failed with exception: {e}", "ERROR")
                results.append(False)
        
        # Generate report
        report = self.generate_report()
        
        return report['summary']['overall_success']

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
ScalPDF Package Testing Suite

Usage:
    python test_packages.py [options]

Options:
    --help    Show this help message

This script runs comprehensive tests on the ScalPDF package system:
- Build environment validation
- Package builder testing
- GUI installer testing
- Smart launcher testing
- Existing package validation

The test results are saved to build/test_report.json
""")
        return
    
    tester = PackageTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
