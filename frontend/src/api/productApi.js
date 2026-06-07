import axios from "axios";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

export const getProducts = (page = 1, search = "") =>
  API.get(`/products?page=${page}&search=${search}`);

export const createProduct = (data) =>
  API.post("/products", data);

export const updateProduct = (id, data) =>
  API.patch(`/products/${id}`, data);

export const deleteProduct = (id) =>
  API.delete(`/products/${id}`);