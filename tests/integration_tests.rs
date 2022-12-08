use std::{path::Path, process::Command};
use tempfile::tempdir;

#[test]
#[cfg_attr(
    windows,
    ignore = "wasmer run cannot map absolute directories on windows"
)]
fn integration_tests() {
    let package_name = "pulldown-cmark";
    let wapm_out = Command::new("cargo")
        .args(["wapm", "--dry-run"])
        .output()
        .expect("Failed to execute command");

    assert!(wapm_out.status.success(), "{wapm_out:?}");

    let temp_dir = tempdir().unwrap();

    let project_dir_path = Path::new(env!("CARGO_MANIFEST_DIR"));
    let wapm_dir = project_dir_path.join("target/wapm");

    assert!(
        wapm_dir.exists(),
        "{}",
        format!("wapm-dir for {} not found", package_name)
    );

    let python_package_dir = temp_dir.path().join("python");
    // Wasmer-pack for generating python bindings
    let output = Command::new("wasmer")
        .current_dir(&wapm_dir)
        .arg("run")
        .arg("wasmer/wasmer-pack-cli@0.5.3")
        .arg("--dir")
        .arg(temp_dir.path())
        .arg("--dir")
        .arg(&wapm_dir)
        .arg("--")
        .arg("python")
        .arg(wapm_dir.join(package_name))
        .arg("--out-dir")
        .arg(&python_package_dir)
        .output()
        .expect("Unable to start wasmer pack. Is it installed ?");

    assert!(output.status.success(), "{output:?}");

    let js_package_dir = temp_dir.path().join("js");
    // generate javascript bindings for the package
    let output = Command::new("wasmer")
        .current_dir(&wapm_dir)
        .arg("run")
        .arg("wasmer/wasmer-pack-cli@0.5.3")
        .arg("--dir")
        .arg(temp_dir.path())
        .arg("--dir")
        .arg(&wapm_dir)
        .arg("--")
        .arg("js")
        .arg(wapm_dir.join(package_name))
        .arg("--out-dir")
        .arg(js_package_dir)
        .output()
        .expect("Unable to start wasmer pack. Is it installed ?");

    assert!(output.status.success(), "{output:?}");

    // create python environment
    let python_env_creation_out = Command::new("python")
        .current_dir(&python_package_dir)
        .args(["-m", "venv", "env"])
        .output()
        .expect("Python environment creation failed");

    assert!(
        python_env_creation_out.status.success(),
        "{python_env_creation_out:?}"
    );

    // create python environment
    let pytest_dir = project_dir_path.join("tests");
    assert!(pytest_dir.exists(), "Error: No test directory found");

    if cfg!(target_os = "windows") {
        let python_pkg_env_dir = python_package_dir.join("env").join("Scripts");

        // install packages in environment using pip
        let pip_out = Command::new("cmd")
            .current_dir(&python_package_dir)
            .args([
                "/C",
                format!("{}", python_pkg_env_dir.join("pip.exe").display()).as_str(),
            ])
            .args(["install", ".", "pytest"])
            .output()
            .expect("msg");

        assert!(pip_out.status.success(), "{pip_out:?}");

        // Run the python tests using pytest and record output
        let pytest_out = Command::new("cmd")
            .current_dir(&python_pkg_env_dir)
            .args([
                "/C",
                format!("{}", python_pkg_env_dir.join("python.exe").display()).as_str(),
            ])
            .arg(pytest_dir.join("main.py"))
            .output()
            .expect("msg");

        assert!(pytest_out.status.success(), "{pytest_out:?}");
    } else {
        let pip_out = Command::new("./env/bin/pip")
            .current_dir(&python_package_dir)
            .args(["install", ".", "pytest"])
            .output()
            .expect("msg");

        assert!(pip_out.status.success(), "{pip_out:?}");

        // Run the python tests using pytest and record output
        let pytest_out = Command::new("./env/bin/pytest")
            .current_dir(&python_package_dir)
            .arg(pytest_dir.join("main.py"))
            .output()
            .expect("msg");

        assert!(pytest_out.status.success(), "{pytest_out:?}");
    }
}
