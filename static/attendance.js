async function api(path, method='GET', body) {
  const opts = {method, headers: {'Content-Type':'application/json'}}
  if (body) opts.body = JSON.stringify(body)
  const res = await fetch(path, opts)
  return res.json()
}

// Pagination & state (server-side)
let currentPage = 1
let totalPages = 1
let pageSize = 10
let courseId = null
let dateVal = null

async function loadCourses(page=1, per_page=100){
  const resp = await api(`/api/courses?page=${page}&per_page=${per_page}`)
  if (!resp.success) return console.warn('Could not load courses')
  const sel = document.getElementById('courseSelect')
  sel.innerHTML = ''
  resp.data.courses.forEach(c => {
    const o = document.createElement('option')
    o.value = c.id
    o.textContent = `${c.course_code} - ${c.course_name}`
    sel.appendChild(o)
  })
}

document.getElementById('courseSearch').addEventListener('input', (e)=>{
  const q = e.target.value.toLowerCase()
  const sel = document.getElementById('courseSelect')
  Array.from(sel.options).forEach(opt=>{
    opt.hidden = q && !opt.text.toLowerCase().includes(q)
  })
})

async function loadCourseStudents(page=1){
  const select = document.getElementById('courseSelect')
  courseId = select.value
  if (!courseId) return alert('Select course')
  dateVal = document.getElementById('attendanceDate').value
  pageSize = parseInt(document.getElementById('pageSize').value,10)
  const dateQuery = dateVal ? `&date=${dateVal}` : ''
  const resp = await api(`/api/attendance/course/${courseId}/today?page=${page}&per_page=${pageSize}${dateQuery}`)
  if (!resp.success) return alert(resp.message || 'Failed')
  currentPage = resp.data.page
  totalPages = resp.data.pages
  renderPage(resp.data.students)
}

function renderPage(students){
  const tbody = document.querySelector('#studentsTable tbody')
  tbody.innerHTML = ''
  students.forEach(s=>{
    const tr = document.createElement('tr')
    const roll = document.createElement('td'); roll.textContent = s.roll_number
    const name = document.createElement('td'); name.textContent = s.name
    const statusTd = document.createElement('td')
    const sel = document.createElement('select')
    ['not_marked','present','absent','late'].forEach(opt => {
      const o = document.createElement('option'); o.value = opt; o.textContent = opt; if (opt===s.status) o.selected=true; sel.appendChild(o)
    })
    statusTd.appendChild(sel)
    tr.appendChild(roll); tr.appendChild(name); tr.appendChild(statusTd)
    tr.dataset.studentId = s.student_id
    tbody.appendChild(tr)
  })
  const pageInfo = document.getElementById('pageInfo')
  pageInfo.textContent = `Page ${currentPage} of ${totalPages}`
}

document.getElementById('loadCourse').addEventListener('click', ()=>{ currentPage=1; loadCourseStudents(1) })
document.getElementById('prevPage').addEventListener('click', ()=>{ if (currentPage>1) loadCourseStudents(currentPage-1) })
document.getElementById('nextPage').addEventListener('click', ()=>{ if (currentPage<totalPages) loadCourseStudents(currentPage+1) })

document.getElementById('attendanceForm').addEventListener('submit', async (e) => {
  e.preventDefault()
  const select = document.getElementById('courseSelect')
  const courseId = select.value
  if (!courseId) return alert('Select course')
  const rows = [...document.querySelectorAll('#studentsTable tbody tr')]
  const dateVal = document.getElementById('attendanceDate').value
  const attendance_records = rows.map(tr => ({
    student_id: tr.dataset.studentId,
    status: tr.querySelector('select').value,
    attendance_date: dateVal ? new Date(dateVal).toISOString() : new Date().toISOString()
  }))
  const resp = await api('/api/attendance', 'POST', {course_id: courseId, attendance_records})
  if (resp.success) alert('Attendance saved')
  else alert(resp.message || 'Error')
})

let chart = null
document.getElementById('loadChart').addEventListener('click', async () => {
  const studentId = document.getElementById('studentId').value.trim()
  const year = parseInt(document.getElementById('year').value,10)
  const month = parseInt(document.getElementById('month').value,10)
  if (!studentId) return alert('Enter student id')
  const resp = await api(`/api/attendance/student/${studentId}/monthly?year=${year}&month=${month}`)
  if (!resp.success) return alert(resp.message || 'Failed')
  const labels = resp.data.days.map(d=>d.toString())
  const values = resp.data.values
  const ctx = document.getElementById('attendanceChart').getContext('2d')
  if (chart) chart.destroy()
  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Attendance (present=1, late=0.5, absent=0)',
        data: values,
        backgroundColor: values.map(v => v===1 ? 'rgba(75,192,192,0.7)' : v===0.5 ? 'rgba(255,206,86,0.7)' : 'rgba(255,99,132,0.7)')
      }]
    },
    options: {
      scales: { y: { beginAtZero: true, max: 1 } }
    }
  })
})

// initial load of courses
loadCourses()
