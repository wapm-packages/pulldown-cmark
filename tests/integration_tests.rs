use std::{fs::File, path::Path, process::Command};
use tempfile::tempdir;

use flate2::write::GzEncoder;
use flate2::Compression;

#[test]
fn integration_tests() {
    let package_name = "pulldown-cmark";
    let wapm_out = Command::new("cargo")
        .args(["wapm", "--dry-run"])
        .output()
        .expect("Failed to execute command");

    assert!(wapm_out.status.success(), "{wapm_out:?}");

    let temp_dir = tempdir().unwrap();

    let project_dir_path = Path::new(env!("CARGO_MANIFEST_DIR"));
    let wapm_dir = project_dir_path.join(format!("target/wapm/{}", package_name));

    assert!(
        wapm_dir.exists(),
        "{}",
        format!("wapm-dir for {} not found", package_name)
    );

    // Create tar.gz
    let tar_gz = File::create(temp_dir.path().join(format!("{}.tar.gz", package_name))).unwrap();
    let enc = GzEncoder::new(tar_gz, Compression::default());
    let mut tar = tar::Builder::new(enc);
    tar.append_dir_all(".", &wapm_dir).unwrap();
    tar.into_inner()
        .expect("Unable to finalise the tar archive")
        .finish()
        .expect("Unable to finalize the gzip encoder");

    // Wasm to pirita convert
    let w2p_out = Command::new("wasmer")
        .current_dir(temp_dir.path())
        .args([
            "run",
            "wapm2pirita",
            "--mapdir",
            format!(".::{}", temp_dir.path().display()).as_str(),
            "--",
            "convert",
        ])
        .arg(format!("{}.tar.gz", package_name))
        .arg(format!("{}.webc", package_name))
        .output()
        .expect("wapm2pirita command failed to execute");

    assert!(w2p_out.status.success(), "{w2p_out:?}");

    // Wasmer-pack for generating python bindings
    let wasmer_pack_out = Command::new("wasmer")
        .current_dir(temp_dir.path())
        .args([
            "run",
            "wasmer-pack",
            "--mapdir",
            format!("f::{}", temp_dir.path().display()).as_str(),
            "--",
            "python",
            &format!("f/{}.webc", package_name),
            "--out-dir",
            &format!("f/python_{}", package_name),
        ])
        .output()
        .expect("wasmer-pack failed to create python binding");

    assert!(wasmer_pack_out.status.success(), "{wasmer_pack_out:?}");

    // check python sha2 dir
    let python_pkg_dir = temp_dir.path().join(format!("python_{}", package_name));
    assert!(python_pkg_dir.exists());

    // create python environment
    let python_env_creation_out = Command::new("python")
        .current_dir(&python_pkg_dir)
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
        let python_pkg_env_dir = python_pkg_dir.join("env").join("Scripts");

        // install packages in environment using pip
        let pip_out = Command::new("cmd")
            .current_dir(&python_pkg_dir)
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
            .current_dir(&python_pkg_dir)
            .args(["install", ".", "pytest"])
            .output()
            .expect("msg");

        assert!(pip_out.status.success(), "{pip_out:?}");

        // Run the python tests using pytest and record output
        let pytest_out = Command::new("./env/bin/pytest")
            .current_dir(&python_pkg_dir)
            .arg(pytest_dir.join("main.py"))
            .output()
            .expect("msg");

        assert!(pytest_out.status.success(), "{pytest_out:?}");
    }
}
