const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');
const xlsx = require('xlsx');
const fetch = require('node-fetch');
const { Low } = require("lowdb");
const { JSONFile } = require("lowdb/node");
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

// Setup lowdb
const file = path.join(__dirname, 'data.json');
const adapter = new JSONFile(file);
const db = new Low(adapter, { books: [], members: [], transactions: [] });

async function initDB() {
  await db.read();
  db.data ||= { books: [], members: [], transactions: [] };
  await db.write();
}
initDB();

app.use(bodyParser.json());
app.use(express.static('public'));

// Books endpoints
app.get('/api/books', async (req, res) => {
  await db.read();
  res.json(db.data.books);
});

app.post('/api/books', async (req, res) => {
  await db.read();
  const book = req.body;
  book.id = Date.now();
  db.data.books.push(book);
  await db.write();
  res.json(book);
});

app.put('/api/books/:id', async (req, res) => {
  await db.read();
  const id = parseInt(req.params.id, 10);
  const idx = db.data.books.findIndex(b => b.id === id);
  if (idx > -1) {
    db.data.books[idx] = { ...db.data.books[idx], ...req.body };
    await db.write();
    res.json(db.data.books[idx]);
  } else {
    res.status(404).send('not found');
  }
});

app.delete('/api/books/:id', async (req, res) => {
  await db.read();
  const id = parseInt(req.params.id, 10);
  db.data.books = db.data.books.filter(b => b.id !== id);
  await db.write();
  res.json({});
});

// Members endpoints
app.get('/api/members', async (req, res) => {
  await db.read();
  res.json(db.data.members);
});

app.post('/api/members', async (req, res) => {
  await db.read();
  const member = req.body;
  member.id = Date.now();
  db.data.members.push(member);
  await db.write();
  res.json(member);
});

app.put('/api/members/:id', async (req, res) => {
  await db.read();
  const id = parseInt(req.params.id, 10);
  const idx = db.data.members.findIndex(m => m.id === id);
  if (idx > -1) {
    db.data.members[idx] = { ...db.data.members[idx], ...req.body };
    await db.write();
    res.json(db.data.members[idx]);
  } else {
    res.status(404).send('not found');
  }
});

app.delete('/api/members/:id', async (req, res) => {
  await db.read();
  const id = parseInt(req.params.id, 10);
  db.data.members = db.data.members.filter(m => m.id !== id);
  await db.write();
  res.json({});
});

// Transactions endpoints
app.get('/api/transactions', async (req, res) => {
  await db.read();
  res.json(db.data.transactions);
});

app.post('/api/transactions', async (req, res) => {
  await db.read();
  const tx = req.body;
  tx.id = Date.now();
  tx.returned = false;
  db.data.transactions.push(tx);
  await db.write();
  res.json(tx);
});

app.put('/api/transactions/:id', async (req, res) => {
  await db.read();
  const id = parseInt(req.params.id, 10);
  const idx = db.data.transactions.findIndex(t => t.id === id);
  if (idx > -1) {
    db.data.transactions[idx] = { ...db.data.transactions[idx], ...req.body };
    await db.write();
    res.json(db.data.transactions[idx]);
  } else {
    res.status(404).send('not found');
  }
});

app.delete('/api/transactions/:id', async (req, res) => {
  await db.read();
  const id = parseInt(req.params.id, 10);
  db.data.transactions = db.data.transactions.filter(t => t.id !== id);
  await db.write();
  res.json({});
});

// Mark transaction as returned
app.post('/api/transactions/:id/return', async (req, res) => {
  await db.read();
  const id = parseInt(req.params.id, 10);
  const tx = db.data.transactions.find(t => t.id === id);
  if (tx) {
    tx.returned = true;
    await db.write();
    res.json(tx);
  } else {
    res.status(404).send('not found');
  }
});

// Overdue list
app.get('/api/overdue', async (req, res) => {
  await db.read();
  const now = Date.now();
  const overdue = db.data.transactions.filter(t => t.returnDate && now > new Date(t.returnDate).getTime() && !t.returned);
  res.json(overdue);
});

// Excel import for books
app.post('/api/import/books', upload.single('file'), async (req, res) => {
  const workbook = xlsx.readFile(req.file.path);
  const sheet = workbook.Sheets[workbook.SheetNames[0]];
  const rows = xlsx.utils.sheet_to_json(sheet);
  await db.read();
  rows.forEach(r => {
    r.id = Date.now() + Math.random();
    db.data.books.push(r);
  });
  await db.write();
  res.json({ count: rows.length });
});

// Excel import for members
app.post('/api/import/members', upload.single('file'), async (req, res) => {
  const workbook = xlsx.readFile(req.file.path);
  const sheet = workbook.Sheets[workbook.SheetNames[0]];
  const rows = xlsx.utils.sheet_to_json(sheet);
  await db.read();
  rows.forEach(r => {
    r.id = Date.now() + Math.random();
    db.data.members.push(r);
  });
  await db.write();
  res.json({ count: rows.length });
});

// Excel import for transactions
app.post('/api/import/transactions', upload.single('file'), async (req, res) => {
  const workbook = xlsx.readFile(req.file.path);
  const sheet = workbook.Sheets[workbook.SheetNames[0]];
  const rows = xlsx.utils.sheet_to_json(sheet);
  await db.read();
  rows.forEach(r => {
    r.id = Date.now() + Math.random();
    r.returned = !!r.returned;
    db.data.transactions.push(r);
  });
  await db.write();
  res.json({ count: rows.length });
});

// Fetch from Google Books / OpenLibrary
app.get('/api/fetchBook/:isbn', async (req, res) => {
  const isbn = req.params.isbn;
  try {
    const google = await fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`);
    const gdata = await google.json();
    if (gdata.items && gdata.items[0]) {
      const info = gdata.items[0].volumeInfo;
      return res.json({
        title: info.title,
        pages: info.pageCount,
        year: info.publishedDate,
        image: info.imageLinks && info.imageLinks.thumbnail,
        category: info.categories && info.categories[0]
      });
    }
    const open = await fetch(`https://openlibrary.org/api/books?bibkeys=ISBN:${isbn}&format=json&jscmd=data`);
    const odata = await open.json();
    const book = odata[`ISBN:${isbn}`];
    if (book) {
      return res.json({
        title: book.title,
        pages: book.number_of_pages,
        year: book.publish_date,
        image: book.cover && book.cover.medium,
        category: book.subjects && book.subjects[0] && book.subjects[0].name
      });
    }
    res.status(404).send('not found');
  } catch (e) {
    res.status(500).send('error');
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
