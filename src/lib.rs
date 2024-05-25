use pyo3::prelude::*;
use rayon::prelude::*;

fn elementwise_squared_difference_i32(vec1: &[i32], vec2: &[i32]) -> i32 {
    assert_eq!(vec1.len(), vec2.len(), "Vectors must be of the same length");

    vec1.iter()
        .zip(vec2.iter())
        .map(|(&x, &y)| (x - y).pow(2))
        .sum()
}

fn elementwise_squared_difference_f64(vec1: &[f64], vec2: &[f64]) -> f64 {
    assert_eq!(vec1.len(), vec2.len(), "Vectors must be of the same length");

    vec1.iter()
        .zip(vec2.iter())
        .map(|(&x, &y)| (x - y).powi(2))
        .sum()
}

#[pyfunction]
fn find_best_tiles_i32(images: Vec<Vec<i32>>, tiles: Vec<Vec<i32>>) -> Vec<usize> {
    images
        .iter()
        .map(|image| find_best_tile_i32(image, &tiles))
        .collect()
}

fn find_best_tile_i32(image: &[i32], tiles: &Vec<Vec<i32>>) -> usize {
    tiles.iter()
        .enumerate()
        .map(|(index, vec)| (index, elementwise_squared_difference_i32(image, vec)))
        .min_by_key(|&(_, diff)| diff)
        .map(|(index, _)| index)
        .unwrap_or(0)
}

#[pyfunction]
fn find_best_tiles_f64(images: Vec<Vec<f64>>, tiles: Vec<Vec<f64>>) -> Vec<usize> {
    images
        .par_iter()
        .map(|image| find_best_tile_f64(image, &tiles, elementwise_squared_difference_f64))
        .collect()
}

fn find_best_tile_f64(image: &[f64], tiles: &Vec<Vec<f64>>, diff_func: fn(&[f64], &[f64]) -> f64) -> usize {
    tiles.par_iter()
        .enumerate()
        .map(|(index, vec)| (index, diff_func(image, vec)))
        .min_by(|&(_, diff1), &(_, diff2)| diff1.partial_cmp(&diff2).unwrap_or(std::cmp::Ordering::Equal))
        .map(|(index, _)| index)
        .unwrap_or(0)
}



/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name="_lib")]
fn rusty_mosaic(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(find_best_tiles_i32, m)?)?;
    m.add_function(wrap_pyfunction!(find_best_tiles_f64, m)?)?;
    Ok(())
}
