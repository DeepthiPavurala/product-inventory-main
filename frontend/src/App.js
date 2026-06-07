import React, { useEffect, useState, useMemo } from "react";
import axios from "axios";
import "./App.css";
import { FiEdit } from "react-icons/fi";
import { FiTrash2 } from "react-icons/fi";
import TaglineSection from "./TaglineSection";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL
});


function App() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({
    id: "",
    name: "",
    description: "",
    category: "",
    price: "",
    quantity: "",
  });
  const [editId, setEditId] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [categories, setCategories] = useState([]);
  const [sortField, setSortField] = useState("created_at");
  const [sortDirection, setSortDirection] = useState("asc");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  
  const fetchCategories = async () => {
    try {
      const res = await api.get("/products/categories");
      //console.log("Fetched categories:", res.data); // 👈 ADD THIS
      setCategories(res.data);
    } catch (err) {
      console.error("Failed to fetch categories", err);
    }
  };
  // Auto-dismiss messages after 5 seconds
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        setMessage("");
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError("");
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleSort = (field) => {
    let newDirection = "asc";

    if (sortField === field && sortDirection === "asc") {
      newDirection = "desc";
    }

    setSortField(field);
    setSortDirection(newDirection);

    fetchProducts(1, filter, field, newDirection);
  };

  // Fetch all products
  const fetchProducts = async (
    pageNumber = 1,
    searchValue = filter,
    sortFieldValue = sortField,
    sortOrderValue = sortDirection,
    categoryValue = selectedCategory
  ) => {
    setLoading(true);
    try {
      const res = await api.get(
        `/products?page=${pageNumber}&limit=5&search=${searchValue}&sort_by=${sortFieldValue}&sort_order=${sortOrderValue}&category=${categoryValue}`
      );

      setProducts(res.data.data);
      setPage(res.data.page);
      setTotalPages(res.data.total_pages);
      setTotal(res.data.total);
      setError("");
    } catch (err) {
      setError("Failed to fetch products");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchProducts(1);
    fetchCategories();
  }, []);


  // Handle form input
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Reset form
  const resetForm = () => {
    setForm({ id: "", name: "", description: "", category:"" , price: "", quantity: "" });
    setEditId(null);
  };

  // Create or update product
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setError("");
    try {
      if (editId) {
        await api.patch(`/products/${editId}`, {
          name: form.name,
          description: form.description,
          category: form.category,
          price: Number(form.price),
          quantity: Number(form.quantity),
        });
        setMessage("Product updated successfully");
      } else {
        await api.post("/products", {
          name: form.name,
          description: form.description,
          category: form.category,
          price: Number(form.price),
          quantity: Number(form.quantity),
        });
        setMessage("Product created successfully");
      }
      resetForm();
      await fetchProducts(page, filter, sortField, sortDirection, selectedCategory);
      await fetchCategories();  
    } catch (err) {
      setError(err.response?.data?.detail || "Operation failed");
      resetForm();
    }
    setLoading(false);
  };

  // Edit product
  const handleEdit = (product) => {
    setForm({
      id: product.id,
      name: product.name,
      description: product.description,
      category: product.category,
      price: product.price,
      quantity: product.quantity,
    });
    setEditId(product.id);
    setMessage("");
    setError("");
  };

  // Delete product
  const handleDelete = async (id) => {
    const ok = window.confirm("Delete this product?");
    if (!ok) return;
    setLoading(true);
    setMessage("");
    setError("");
    try {
      await api.delete(`/products/${id}`);
      setMessage("Product deleted successfully");
      fetchProducts(page, filter, sortField, sortDirection);
    } catch (err) {
      setError("Delete failed");
    }
    setLoading(false);
  };

  const currency = (n) =>
    typeof n === "number" ? n.toFixed(2) : Number(n || 0).toFixed(2);

  return (
    <div className="app-bg">
      <header className="topbar">
        <div className="brand">
          <span className="brand-badge">📦</span>
          <h1>Product Inventory</h1>
        </div>
        <div className="top-actions">
          <button
            className="btn btn-light"
            onClick={() => fetchProducts(page, filter, sortField, sortDirection)
            }
            disabled={loading}
          >
            Refresh
          </button>
        </div>
      </header>

      <div className="container">
        <div className="stats-bar">
          <div className="stats">

            <div className="left-stats">
              <div className="chip">Total: {total}</div>
            </div>

            <div className="right-filters">
              {/* Search */}
              <input
                type="text"
                placeholder="Search by id, name or description..."
                value={filter}
                onChange={(e) => {
                  const value = e.target.value;
                  setFilter(value);
                  fetchProducts(1, value, sortField, sortDirection, selectedCategory);
                }}
              />

              {/* Category Dropdown */}
              <select
                value={selectedCategory}
                onChange={(e) => {
                  const value = e.target.value;
                  setSelectedCategory(value);
                  fetchProducts(1, filter, sortField, sortDirection, value);
                }}
              >
                <option value="">All Categories</option>

                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

          </div>
        </div>


        <div className="content-grid">
          <div className="card form-card">
            <h2>{editId ? "Edit Product" : "Add Product"}</h2>
            <form onSubmit={handleSubmit} className="product-form">
              <input
                type="text"
                name="name"
                placeholder="Name"
                value={form.name}
                onChange={handleChange}
                required
              />
              <input
                type="text"
                name="description"
                placeholder="Description"
                value={form.description}
                onChange={handleChange}
                required
              />
              <input
                type="text"
                name="category"
                placeholder="Category"
                value={form.category}
                onChange={handleChange}
                required
              />
              <input
                type="number"
                name="price"
                placeholder="Price"
                value={form.price}
                onChange={handleChange}
                required
                step="0.01"
              />
              <input
                type="number"
                name="quantity"
                placeholder="Quantity"
                value={form.quantity}
                onChange={handleChange}
                required
              />
              <div className="form-actions">
                <button className="btn" type="submit" disabled={loading}>
                  {editId ? "Update" : "Add"}
                </button>
                {editId && (
                  <button
                    className="btn btn-secondary"
                    type="button"
                    onClick={() => {
                      resetForm();
                      setMessage("");
                      setError("");
                    }}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
            {message && <div className="success-msg">{message}</div>}
            {error && <div className="error-msg">{error}</div>}
          </div>
          
          <TaglineSection />

          <div className="card list-card">
            <h2>Products</h2>
            {loading ? (
              <div className="loader">Loading...</div>
            ) : (
              <div className="scroll-x">
                <table className="product-table">
                  <thead>
                    <tr>
                      <th 
                        className={`sortable ${sortField === 'id' ? `sort-${sortDirection}` : ''}`}
                        onClick={() => handleSort('id')}
                      >
                        ID
                      </th>
                      <th 
                        className={`sortable ${sortField === 'name' ? `sort-${sortDirection}` : ''}`}
                        onClick={() => handleSort('name')}
                      >
                        Name
                      </th>
                      <th>Description</th>
                      <th onClick={() => handleSort("category")}>Category</th> 
                      <th 
                        className={`sortable ${sortField === 'price' ? `sort-${sortDirection}` : ''}`}
                        onClick={() => handleSort('price')}
                      >
                        Price
                      </th>
                      <th 
                        className={`sortable ${sortField === 'quantity' ? `sort-${sortDirection}` : ''}`}
                        onClick={() => handleSort('quantity')}
                      >
                        Quantity
                      </th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((p) => (
                      <tr key={p.id}>
                        <td>{p.id}</td>
                        <td className="name-cell">{p.name}</td>
                        <td className="desc-cell" title={p.description}>{p.description}</td>
                        <td className="cat-cell" title={p.category}>{p.category}</td>
                        <td className="price-cell">${currency(p.price)}</td>
                        <td>
                          <span className="qty-badge">{p.quantity}</span>
                        </td>
                        <td>
                          <div className="row-actions">
                            <button className="icon-btn edit-icon" onClick={() => handleEdit(p)} title="Edit Product">
                              <FiEdit />
                            </button>
                            <button className="icon-btn delete-icon" onClick={() => handleDelete(p.id)} title="Delete Product">
                              <FiTrash2 />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {products.length === 0 && (
                      <tr>
                        <td colSpan={7} className="empty">
                          No products found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
              <div style={{ marginTop: "20px", textAlign: "center" }}>
                <button
                  disabled={page === 1}
                  onClick={() => 
                    fetchProducts(page - 1, filter, sortField, sortDirection)
                  }
                >
                  Prev
                </button>

                <span style={{ margin: "0 15px" }}>
                  Page {page} of {totalPages}
                </span>

                <button
                  disabled={page === totalPages || total === 0}
                  onClick={() => fetchProducts(page + 1, filter, sortField, sortDirection)}
                >
                  Next
                </button>
              </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
