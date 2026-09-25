import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../lib/authContext";
import { extractErrorMessage } from "../../lib/api";
import { 
  ShieldCheck, 
  Mail, 
  Lock, 
  User, 
  GraduationCap, 
  Building2, 
  BookOpen, 
  Calendar, 
  Award,
  ArrowRight,
  AlertCircle,
  Clock,
  CheckCircle2
} from "lucide-react";

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [role, setRole] = useState<"student" | "recruiter" | "college_admin">("student");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Role-specific fields
  const [collegeName, setCollegeName] = useState("");
  const [department, setDepartment] = useState("Computer Science & Engineering");
  const [graduationYear, setGraduationYear] = useState<string>("2026");
  const [cgpa, setCgpa] = useState<string>("8.5");
  const [companyName, setCompanyName] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isRegistered, setIsRegistered] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const trimmedEmail = email.trim().toLowerCase();
    const trimmedName = fullName.trim();
    if (!trimmedEmail || !password || !trimmedName) {
      setError("Please fill out all required fields.");
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      setLoading(false);
      return;
    }

    const payload: any = {
      full_name: trimmedName,
      email: trimmedEmail,
      password,
      role
    };

    if (role === "student") {
      payload.college_name = collegeName.trim() || "Delhi Technological University";
      payload.department = department.trim() || "Computer Science & Engineering";
      const parsedGradYear = parseInt(graduationYear, 10);
      payload.graduation_year = !isNaN(parsedGradYear) ? parsedGradYear : 2026;
      const parsedCgpa = parseFloat(cgpa);
      payload.cgpa = !isNaN(parsedCgpa) ? parsedCgpa : 8.0;
    } else if (role === "recruiter") {
      payload.company_name = companyName.trim() || "TechCorp Global";
    } else if (role === "college_admin") {
      payload.college_name = collegeName.trim() || "National Institute of Technology";
    }

    try {
      const resp = await register(payload);
      if (resp?.approval_status === "APPROVED") {
        if (resp.role === "recruiter") {
          navigate("/recruiter/dashboard");
        } else if (resp.role === "college_admin") {
          navigate("/college/dashboard");
        } else if (resp.role === "platform_admin") {
          navigate("/admin/dashboard");
        } else {
          navigate("/student/dashboard");
        }
      } else {
        setIsRegistered(true);
      }
    } catch (err: any) {
      setError(extractErrorMessage(err, "Registration failed. Please check inputs and try again."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[350px] bg-indigo-500/10 blur-[130px] rounded-full pointer-events-none -z-10" />

      <div className="w-full max-w-lg space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center mx-auto shadow-lg shadow-indigo-500/25">
            <ShieldCheck className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Create a Career<span className="text-indigo-400">Lens</span> Account
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Join the verified recruitment ecosystem for students, recruiters, and placement cells
          </p>
        </div>

        {/* Role Selector Tabs */}
        <div className="p-1.5 rounded-2xl bg-slate-800/80 border border-slate-700 grid grid-cols-3 gap-1.5 text-xs font-semibold">
          <button
            type="button"
            onClick={() => setRole("student")}
            className={`py-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
              role === "student"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <GraduationCap size={15} />
            <span>Student</span>
          </button>

          <button
            type="button"
            onClick={() => setRole("recruiter")}
            className={`py-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
              role === "recruiter"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Building2 size={15} />
            <span>Recruiter</span>
          </button>

          <button
            type="button"
            onClick={() => setRole("college_admin")}
            className={`py-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
              role === "college_admin"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Award size={15} />
            <span>College TPO</span>
          </button>
        </div>

        {isRegistered ? (
          <div className="p-6 sm:p-8 rounded-3xl bg-slate-800/50 border border-slate-700/80 shadow-2xl text-center space-y-5 animate-in fade-in zoom-in-95 duration-300">
            <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto text-amber-400 shadow-lg shadow-amber-500/10">
              <Clock className="w-8 h-8 animate-pulse" />
            </div>
            
            <div className="space-y-2">
              <span className="inline-block px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-500/30">
                Pending Administrator Approval
              </span>
              <h2 className="text-xl sm:text-2xl font-bold text-white">Registration Submitted</h2>
              <p className="text-xs sm:text-sm text-slate-300 max-w-sm mx-auto leading-relaxed">
                Registration successful. Your account is pending administrator approval. You will be able to access CareerLens after administrator approval.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-700/70 text-left space-y-2 text-xs">
              <div className="text-slate-400 text-[11px] font-medium">Submitted Profile:</div>
              <div className="text-white font-semibold flex items-center justify-between">
                <span>{fullName}</span>
                <span className="text-[10px] font-mono uppercase bg-slate-800 px-2 py-0.5 rounded text-indigo-300 border border-slate-700">
                  {role === "student" ? "Student" : (role === "recruiter" ? "Recruiter" : "College TPO")}
                </span>
              </div>
              <div className="text-slate-400 font-mono text-[11px]">{email}</div>
            </div>

            <div className="pt-2">
              <Link
                to="/login"
                className="w-full py-3 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2"
              >
                <span>Return to Sign In</span>
                <ArrowRight size={15} />
              </Link>
            </div>
          </div>
        ) : (
          <div className="p-6 sm:p-8 rounded-3xl bg-slate-800/50 border border-slate-700/80 shadow-2xl space-y-5">
            {error && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle size={15} className="text-rose-400 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Full Legal Name
                </label>
                <div className="relative">
                  <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    placeholder="e.g. Priya Sharma"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="email"
                    placeholder="priya@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="password"
                    placeholder="Minimum 6 characters"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>
              </div>

              {/* Student Specific Fields */}
              {role === "student" && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      College / University Name
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. IIIT Delhi, DTU, NIT Trichy"
                      value={collegeName}
                      onChange={(e) => setCollegeName(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                        Department
                      </label>
                      <input
                        type="text"
                        value={department}
                        onChange={(e) => setDepartment(e.target.value)}
                        className="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                        Grad Year
                      </label>
                      <input
                        type="number"
                        value={graduationYear}
                        onChange={(e) => setGraduationYear(e.target.value)}
                        className="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                        CGPA
                      </label>
                      <input
                        type="text"
                        inputMode="decimal"
                        placeholder="e.g. 7.6"
                        value={cgpa}
                        onChange={(e) => setCgpa(e.target.value)}
                        className="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
                        required
                      />
                    </div>
                  </div>
                </>
              )}

              {/* Recruiter Specific Fields */}
              {role === "recruiter" && (
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Hiring Company Name
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Google, TechCorp, Microsoft"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>
              )}

              {/* College Admin Specific Fields */}
              {role === "college_admin" && (
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Institution / University Name
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Indian Institute of Information Technology"
                    value={collegeName}
                    onChange={(e) => setCollegeName(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50 transition-colors shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2 mt-2"
              >
                <span>{loading ? "Creating Account..." : `Register as ${role === "student" ? "Student" : (role === "recruiter" ? "Recruiter" : "College TPO")}`}</span>
                <ArrowRight size={15} />
              </button>
            </form>

            <div className="pt-4 border-t border-slate-700/60 text-center text-xs text-slate-400">
              Already have an account?{" "}
              <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-semibold underline underline-offset-2">
                Sign In
              </Link>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
